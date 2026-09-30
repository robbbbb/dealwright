"""Card 2 — admin smoke (catalog CRUD is admin-covered in MVP, design-log)."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from catalog.tests.conftest import make_service, make_user


def _superuser() -> User:
    return User.objects.create_superuser(
        username="admin", email="a@example.com", password="pw12345!x"
    )


def test_changelist_renders(db, client: Client) -> None:
    client.force_login(_superuser())
    make_service(make_user())
    response = client.get(reverse("admin:catalog_service_changelist"))
    assert response.status_code == 200
    assert b"Test service" in response.content


def test_add_page_with_skill_inline(db, client: Client) -> None:
    client.force_login(_superuser())
    response = client.get(reverse("admin:catalog_service_add"))
    assert response.status_code == 200
    assert b"required_skills" in response.content.lower()
