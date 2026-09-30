"""Seed the default skill vocabulary for one provider (draft-catalog-derived).

Thin wrapper: data in team.seed_data, write path in team.services
(seed_default_skills) — same pattern as catalog's seed_catalog.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from team import services


class Command(BaseCommand):
    help = "Seed the default skill registry (union of the service catalog draft) for one user."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "username", help="User whose registry gets the seed (provider tenancy)."
        )


    def handle(self, *args: Any, **options: Any) -> None:
        try:
            owner = User.objects.get(username=options["username"])
        except User.DoesNotExist:
            raise CommandError(
                f"No user '{options['username']}' — pass an existing provider's username."
            ) from None
        created, total = services.seed_default_skills(owner=owner)
        self.stdout.write(
            self.style.SUCCESS(
                f"Skill seed for '{owner.username}': {created} created, "
                f"{total - created} already present (edits preserved)."
            )
        )
