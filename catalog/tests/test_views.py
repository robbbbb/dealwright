"""Catalog UI tests — public API only (login, list, seed, CRUD, skills, tenancy)."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from catalog import services
from catalog.tests.conftest import VALID_SERVICE, make_user
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
        "category": "Content & Social",
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

    def test_other_users_services_not_listed(self, client) -> None:
        _client_for(client, "mine")
        other = make_user("other")
        services.create_service(owner=other, **VALID_SERVICE)
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



class TestServiceCreate:
    def test_get_renders_form(self, client) -> None:
        _client_for(client)
        response = client.get(reverse("catalog:service_create"))
        assert response.status_code == 200
        assert "currency" in response.content.decode()

    def test_post_creates_service_with_parsed_tags(self, client) -> None:
        pro = _client_for(client)
        response = client.post(reverse("catalog:service_create"), _service_data())
        assert response.status_code == 302
        service = pro.services.get(name="Social calendar")
        assert service.problem_tags == ["leads-lost", "slow-response"]
        assert service.currency == "PHP"

    def test_invalid_data_shows_error_and_creates_nothing(self, client) -> None:
        pro = _client_for(client)
        response = client.post(
            reverse("catalog:service_create"), _service_data(currency="usd")
        )
        assert response.status_code == 200
        assert "currency" in response.context["form"].errors
        assert pro.services.count() == 0

    def test_requires_login(self, client) -> None:
        assert client.get(reverse("catalog:service_create")).status_code == 302


class TestServiceEdit:
    def test_edit_own_service(self, client) -> None:
        pro = _client_for(client)
        service = services.create_service(owner=pro, **VALID_SERVICE)
        response = client.post(
            _url("service_edit", service),
            _service_data(name="Renamed"),
        )
        assert response.status_code == 302
        service.refresh_from_db()
        assert service.name == "Renamed"

    def test_other_users_service_is_404(self, client) -> None:
        _client_for(client, "mine")
        other = make_user("other")
        service = services.create_service(owner=other, **VALID_SERVICE)
        assert (
            client.get(_url("service_edit", service)).status_code
            == 404
        )

    def test_edit_page_lists_required_skills_and_add_form(self, client) -> None:
        pro = _client_for(client)
        service = services.create_service(owner=pro, **VALID_SERVICE)
        response = client.get(_url("service_edit", service))
        assert "Required skills" in response.content.decode()


class TestServiceDelete:
    def test_post_deletes_own(self, client) -> None:
        pro = _client_for(client)
        service = services.create_service(owner=pro, **VALID_SERVICE)
        url = _url("service_delete", service)
        assert client.post(url).status_code == 302
        assert pro.services.count() == 0

    def test_get_rejected(self, client) -> None:
        pro = _client_for(client)
        service = services.create_service(owner=pro, **VALID_SERVICE)
        assert client.get(_url("service_delete", service)).status_code == 405


class TestRequiredSkills:
    def test_add_and_remove_skill(self, client) -> None:
        pro = _client_for(client)
        service = services.create_service(owner=pro, **VALID_SERVICE)
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
        service = services.create_service(owner=pro, **VALID_SERVICE)
        assert client.get(_url("skill_add", service)).status_code == 405

    def test_cannot_touch_other_users_skill(self, client) -> None:
        _client_for(client, "mine")
        other = make_user("other")
        service = services.create_service(owner=other, **VALID_SERVICE)
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
