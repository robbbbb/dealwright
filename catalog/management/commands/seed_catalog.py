"""Seed the default catalog for one provider (docs/design/service-catalog-draft.md).

Thin wrapper: the data lives in catalog.seed_data, the write path in
catalog.services.seed_default_catalog (shared with the in-app action).
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from catalog import services


class Command(BaseCommand):
    help = "Seed the default service catalog (docs/design/service-catalog-draft.md) for one user."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("username", help="User whose catalog gets the seed (provider tenancy).")

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            owner = User.objects.get(username=options["username"])
        except User.DoesNotExist:
            raise CommandError(
                f"No user '{options['username']}' — pass an existing provider's username."
            ) from None
        created, total = services.seed_default_catalog(owner=owner)
        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog seed for '{owner.username}': {created} created, "
                f"{total - created} already present (edits preserved)."
            )
        )
