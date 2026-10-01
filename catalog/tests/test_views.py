"""Catalog UI tests — public API only (login, list, seed, CRUD, skills, tenancy)."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from catalog import services
from catalog.tests.conftest import VALID_SERVICE, category_for, make_service, make_user
from team.models import Skill


def _url(name: str, service, skill: str | None = None) -> str:
    """Reverse a service-scoped route with canonical slugs."""
    from django.utils.text import slugify

    kwargs = {"category": slugify(service.category), "service": service.slug}
    if skill is not None:
        kwargs["skill"] = skill
    return reverse(f"catalog:{name}", kwargs=kwargs)

pytestmark = pytest.mark.django_db


def _client_for(client: object, username: str = "pro") -> User:
    user = User.objects.create_user(username=username, password="pw12345!x")
    client.login(username=username, password="pw12345!x")
    return user


def _service_data(**overrides: object) -> dict[str, object]:
    data = {
        "category": "",  # tests pass the pk of a category created for the user
        "name": "Social calendar",
        "currency": "PHP",
        "setup_low": "4000",
        "setup_high": "8000",
        "monthly_low": "1500",
        "monthly_high": "3000",
        "custom_quote": False,
        "delivery_days_min": "14",
        "delivery_days_max": "21",
        "tags_text": "leads-lost, slow-response",
    }
    return {**data, **overrides}


class TestServiceList:
    def test_requires_login(self, client) -> None:
        assert client.get(reverse("catalog:service_list")).status_code == 302

    def test_shows_services_and_prices(self, client) -> None:
        pro = _client_for(client)
        services.seed_default_catalog(owner=pro)
        response = client.get(reverse("catalog:service_list"))
        assert response.status_code == 200
        html = response.content.decode()
        assert "Podcast distribution pipeline" in html
        assert "setup ₱4,000–8,000 · retainer ₱1,500–3,000/mo" in html
        assert "ready to quote" in html
        assert "Browse services" in html

    def test_other_users_services_not_listed(self, client) -> None:
        _client_for(client, "mine")
        other = make_user("other")
        make_service(other)
        html = client.get(reverse("catalog:service_list")).content.decode()
        assert VALID_SERVICE["name"] not in html

    def test_empty_state_shows_seed_button(self, client) -> None:
        _client_for(client)
        html = client.get(reverse("catalog:service_list")).content.decode()
        assert "Load default catalog" in html


class TestSeedDefaults:
    def test_post_loads_missing_only(self, client) -> None:
        pro = _client_for(client)
        client.post(reverse("catalog:seed_defaults"))
        assert client.post(reverse("catalog:seed_defaults")).status_code == 302
        assert pro.services.count() == 25

    def test_get_rejected(self, client) -> None:
        _client_for(client)
        assert client.get(reverse("catalog:seed_defaults")).status_code == 405



class TestCategoryAdd:
    def test_requires_login(self, client) -> None:
        assert client.get(reverse("catalog:category_add")).status_code == 302

    def test_get_renders_form(self, client) -> None:
        _client_for(client)
        response = client.get(reverse("catalog:category_add"))
        assert response.status_code == 200
        assert "Category name" in response.content.decode()

    def test_post_creates_and_redirects_to_catalog(self, client) -> None:
        pro = _client_for(client)
        response = client.post(
            reverse("catalog:category_add"), {"name": "Content & Social"}
        )
        assert response.status_code == 302
        assert response.url == reverse("catalog:service_list")
        assert pro.service_categories.filter(name="Content & Social").exists()

    def test_duplicate_name_is_idempotent(self, client) -> None:
        pro = _client_for(client)
        category_for(pro, "Content & Social")
        assert (
            client.post(
                reverse("catalog:category_add"), {"name": "Content & Social"}
            ).status_code
            == 302
        )
        assert pro.service_categories.count() == 1

    def test_blank_name_rerenders_with_error(self, client) -> None:
        pro = _client_for(client)
        response = client.post(reverse("catalog:category_add"), {"name": "  "})
        assert response.status_code == 200
        assert "name" in response.context["form"].errors
        assert pro.service_categories.count() == 0

    def test_service_form_select_lists_only_owner_categories(self, client) -> None:
        pro = _client_for(client)
        category_for(pro, "Mine only")
        category_for(make_user("other-cats"), "Foreign cat")
        html = client.get(reverse("catalog:service_create")).content.decode()
        assert "Mine only" in html
        assert "Foreign cat" not in html

    def test_create_page_hints_when_no_categories(self, client) -> None:
        _client_for(client)
        html = client.get(reverse("catalog:service_create")).content.decode()
        assert "add your first category" in html


class TestServiceCreate:
    def test_get_renders_form(self, client) -> None:
        _client_for(client)
        response = client.get(reverse("catalog:service_create"))
        assert response.status_code == 200
        assert "currency" in response.content.decode()

    def test_post_creates_service_with_parsed_tags(self, client) -> None:
        pro = _client_for(client)
        category = category_for(pro, "Content & Social")
        response = client.post(
            reverse("catalog:service_create"), _service_data(category=category.pk)
        )
        assert response.status_code == 302
        service = pro.services.get(name="Social calendar")
        assert service.problem_tags == ["leads-lost", "slow-response"]
        assert service.currency == "PHP"
        assert service.category.name == "Content & Social"

    def test_post_without_category_shows_error(self, client) -> None:
        pro = _client_for(client)
        response = client.post(reverse("catalog:service_create"), _service_data())
        assert response.status_code == 200
        assert "category" in response.context["form"].errors
        assert pro.services.count() == 0

    def test_post_cross_owner_category_pk_is_invalid_choice(self, client) -> None:
        """Tenancy through the form: another provider's category pk is never a
        valid choice (pass 11 review probe, locked as a test)."""
        pro = _client_for(client)
        foreign = category_for(make_user("tenancy-probe"), "Foreign cat")
        response = client.post(
            reverse("catalog:service_create"),
            _service_data(category=foreign.pk),
        )
        assert response.status_code == 200
        assert "category" in response.context["form"].errors
        assert pro.services.count() == 0

    def test_invalid_data_shows_error_and_creates_nothing(self, client) -> None:
        pro = _client_for(client)
        category = category_for(pro, "Content & Social")
        response = client.post(
            reverse("catalog:service_create"),
            _service_data(category=category.pk, currency="usd"),
        )
        assert response.status_code == 200
        assert "currency" in response.context["form"].errors
        assert pro.services.count() == 0

    def test_requires_login(self, client) -> None:
        assert client.get(reverse("catalog:service_create")).status_code == 302


class TestServiceEdit:
    def test_edit_own_service(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        response = client.post(
            _url("service_edit", service),
            _service_data(name="Renamed", category=service.category_id),
        )
        assert response.status_code == 302
        service.refresh_from_db()
        assert service.name == "Renamed"

    def test_other_users_service_is_404(self, client) -> None:
        _client_for(client, "mine")
        other = make_user("other")
        service = make_service(other)
        assert (
            client.get(_url("service_edit", service)).status_code
            == 404
        )

    def test_edit_page_lists_required_skills_and_add_form(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        response = client.get(_url("service_edit", service))
        html = response.content.decode()
        assert "Service details" in html
        assert "Pricing" in html
        assert "Delivery window" in html
        assert "Required skills" in html
        assert "Danger zone" in html
        assert html.index("Required skills") < html.index("Danger zone")

    def test_destructive_actions_ask_for_confirmation(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        skill = Skill.objects.create(owner=pro, name="CRM management")
        services.add_required_skill(service=service, skill=skill, min_level="beginner")

        html = client.get(_url("service_edit", service)).content.decode()

        assert (
            "data-confirm='Delete \"Test service\"? This cannot be undone.'" in html
        )
        assert "data-confirm='Remove the \"CRM management\" requirement?'" in html


class TestServiceDelete:
    def test_post_deletes_own(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        url = _url("service_delete", service)
        assert client.post(url).status_code == 302
        assert pro.services.count() == 0

    def test_get_rejected(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        assert client.get(_url("service_delete", service)).status_code == 405


class TestRequiredSkills:
    def test_add_and_remove_skill(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        skill = Skill.objects.create(owner=pro, name="CRM management")
        client.post(
            _url("skill_add", service),
            {"skill": skill.pk, "min_level": "intermediate"},
        )
        assert service.required_skills.get().skill == skill
        skill_slug = service.required_skills.get().slug
        assert (
            client.post(_url("skill_delete", service, skill_slug)).status_code
            == 302
        )
        assert service.required_skills.count() == 0

    def test_skill_add_get_rejected(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        assert client.get(_url("skill_add", service)).status_code == 405

    def test_cannot_touch_other_users_skill(self, client) -> None:
        _client_for(client, "mine")
        other = make_user("other")
        service = make_service(other)
        skill = Skill.objects.create(owner=other, name="Copywriting")
        services.add_required_skill(service=service, skill=skill, min_level="advanced")
        skill_slug = service.required_skills.get().slug
        assert (
            client.post(_url("skill_delete", service, skill_slug)).status_code
            == 404
        )


class TestSidebarWiring:
    def test_app_sidebar_links_catalog(self, client) -> None:
        _client_for(client)
        html = client.get(reverse("catalog:service_list")).content.decode()
        assert 'href="/catalog/"' in html
        assert "Coming soon" not in html.split("Service catalog")[0][-400:]

class TestSlugSemantics:
    def test_slug_frozen_on_rename(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        created_slug = service.slug
        services.update_service(service=service, name="Totally new name")
        service.refresh_from_db()
        assert service.slug == created_slug  # renames never break links

    def test_same_name_cross_category_gets_suffix(self, client) -> None:
        pro = _client_for(client)
        first = make_service(pro)
        second_cat = category_for(pro, "Automated follow-ups")
        second = services.create_service(
            owner=pro, **{**VALID_SERVICE, "category": second_cat}
        )
        assert first.slug != second.slug
        assert second.slug.startswith(first.slug + "-")

    def test_cross_owner_same_slug_allowed(self, client) -> None:
        from catalog.models import Service

        mine = _client_for(client, "mine")
        other = make_user("other-slug")
        a = make_service(mine)
        b = make_service(other)
        assert a.slug == b.slug  # uniqueness is per owner, not global
        assert Service.objects.filter(slug=a.slug).count() == 2

    def test_wrong_category_slug_is_404(self, client) -> None:
        pro = _client_for(client)
        service = make_service(pro)
        url = reverse(
            "catalog:service_edit",
            kwargs={"category": "not-the-real-category", "service": service.slug},
        )
        assert client.get(url).status_code == 404
