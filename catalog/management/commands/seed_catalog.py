"""Seed the default catalog from docs/design/service-catalog-draft.md (Card 2).

Idempotent and edit-safe: services are keyed on (owner, category, name) and
only *missing* rows are created — provider customizations (Tier 0) are never
overwritten by a re-run. Every row passes full_clean; the test suite asserts
that, so a bad transcription fails loudly.

Notes on transcription choices (from the draft):
- ROI lever fields were REMOVED from the model (Robb, 2026-09-30, design-log)
  — the catalog is services + prices + delivery + skills only, no computation.
- "Verified only" (draft, cat 7 Django builds) maps to ``advanced`` on the
  team proficiency ladder (design-log deviation 2026-09-29).
- "30–80k custom" (internal tools) keeps its numeric anchor plus custom_quote.
- "— / by hrs" (personal assistant staffing) = custom_quote, no ranges.
- Delivery ranges converted from weeks to days; "immediate" = 0.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from catalog.models import RequiredSkill, Service

D = Decimal

B = "beginner"  # default proficiency floor for most catalog skills
A = "advanced"  # draft's "Verified only" — Django builds

# (skill, min_level) per draft's "VA skills:" lines.
CAT1 = [("CRM management (GHL/Zoho/HubSpot)", B), ("Form builders", B), ("n8n monitoring", B)]
CAT2 = [("Email marketing", B), ("Messenger/WhatsApp tools", B), ("Copy review", B)]
CAT3 = [("Customer support", B), ("Helpdesk tools", B), ("Empathy-tone review", B)]
CAT4 = [("Spreadsheets", B), ("Basic bookkeeping", B), ("n8n monitoring", B)]
CAT5 = [
    ("Podcast admin", B), ("AI content review", B),
    ("Email marketing", B), ("Sensitive-content care", B),
]
CAT6 = [("Social management", B), ("Community engagement", B), ("Copy", B)]
CAT7 = [("Django/full-stack development", A)]
CAT8 = [("Calendar management", B), ("Task systems", B), ("Calls & bookings", B), ("Discretion", B)]

SERVICES: list[dict[str, Any]] = [
    # --- 1. Lead capture & CRM automation ---
    dict(
        category="Lead capture & CRM automation",
        name="Lead centralization funnel (FB/IG/WhatsApp/web → CRM)",
        problem_tags=["leads-lost", "dm-backlog"],
        setup=(8000, 15000), monthly=(2000, 4000), delivery=(7, 14), skills=CAT1,
    ),
    dict(
        category="Lead capture & CRM automation",
        name="Speed-to-lead auto-response + booking link",
        problem_tags=["slow-response"],
        setup=(5000, 10000), monthly=(1500, 3000), delivery=(7, 7), skills=CAT1,
    ),
    dict(
        category="Lead capture & CRM automation",
        name="CRM pipeline setup & cleanup",
        problem_tags=["follow-up-gap", "data-hygiene"],
        setup=(6000, 12000), monthly=(1500, 3000), delivery=(7, 14), skills=CAT1,
    ),
    # --- 2. Automated follow-ups ---
    dict(
        category="Automated follow-ups",
        name="Follow-up sequences (5–9 touches, multi-channel)",
        problem_tags=["follow-up-gap", "leads-lost"],
        setup=(7000, 14000), monthly=(2000, 4000), delivery=(7, 14), skills=CAT2,
    ),
    dict(
        category="Automated follow-ups",
        name="Appointment reminders & confirmations",
        problem_tags=["no-shows"],
        setup=(4000, 8000), monthly=(1500, 3000), delivery=(7, 7), skills=CAT2,
    ),
    dict(
        category="Automated follow-ups",
        name="Quote & proposal chase flow",
        problem_tags=["follow-up-gap", "slow-response"],
        setup=(5000, 9000), monthly=(1500, 3000), delivery=(7, 7), skills=CAT2,
    ),
    # --- 3. Customer support & onboarding ---
    dict(
        category="Customer support & onboarding",
        name="FAQ triage inbox + auto-responder",
        problem_tags=["support-repeat"],
        setup=(6000, 12000), monthly=(2000, 4000), delivery=(7, 14), skills=CAT3,
    ),
    dict(
        category="Customer support & onboarding",
        name="Client onboarding workflow (docs, welcome, kickoff)",
        problem_tags=["churn-risk"],
        setup=(8000, 15000), monthly=(2000, 4000), delivery=(14, 14), skills=CAT3,
    ),
    dict(
        category="Customer support & onboarding",
        name="Review & feedback collection",
        problem_tags=["churn-risk", "reputation"],
        setup=(4000, 8000), monthly=(1000, 2000), delivery=(7, 7), skills=CAT3,
    ),
    # --- 4. Reporting, invoices, dashboards & data entry ---
    dict(
        category="Reporting, invoices, dashboards & data entry",
        name="Invoice + payment reminder automation",
        problem_tags=["late-payments"],
        setup=(6000, 12000), monthly=(1500, 3000), delivery=(7, 7), skills=CAT4,
    ),
    dict(
        category="Reporting, invoices, dashboards & data entry",
        name="Weekly auto-reports (sales/pipeline/content)",
        problem_tags=["admin-burden"],
        setup=(8000, 18000), monthly=(2000, 4000), delivery=(7, 14), skills=CAT4,
    ),
    dict(
        category="Reporting, invoices, dashboards & data entry",
        name="Data sync & entry automation (form → system)",
        problem_tags=["data-rekey"],
        setup=(6000, 14000), monthly=(1500, 3000), delivery=(7, 14), skills=CAT4,
    ),
    # --- 5. Podcast & content distribution ---
    dict(
        category="Podcast & content distribution",
        # noqa on next line: full draft name kept verbatim
        name="Podcast distribution pipeline (episode → email/captions/questions → approval → channels)",  # noqa: E501
        problem_tags=["content-reuse"],
        setup=(12000, 20000), monthly=(3000, 6000), delivery=(14, 21), skills=CAT5,
    ),
    dict(
        category="Podcast & content distribution",
        name="Content repurposing engine (1 long video → clips/quotes/blog)",
        problem_tags=["content-reuse"],
        setup=(10000, 18000), monthly=(3000, 5000), delivery=(14, 14), skills=CAT5,
    ),
    dict(
        category="Podcast & content distribution",
        name="Newsletter production automation",
        problem_tags=["inconsistent-content"],
        setup=(6000, 12000), monthly=(2000, 4000), delivery=(7, 14), skills=CAT5,
    ),
    # --- 6. Social media management & scheduling ---
    dict(
        category="Social media management & scheduling",
        name="Batch scheduling + content calendar (VA-operated)",
        problem_tags=["inconsistent-content"],
        setup=(5000, 10000), monthly=(2500, 5000), delivery=(7, 7), skills=CAT6,
    ),
    dict(
        category="Social media management & scheduling",
        name="DM & comment triage (VA + auto-routes)",
        problem_tags=["dm-backlog"],
        setup=(5000, 9000), monthly=(2000, 4000), delivery=(7, 7), skills=CAT6,
    ),
    dict(
        category="Social media management & scheduling",
        name="Mention & keyword alerts",
        problem_tags=["reputation"],
        setup=(4000, 7000), monthly=(1000, 2000), delivery=(7, 7), skills=CAT6,
    ),
    # --- 7. Custom Django dashboards, portals & internal tools ---
    dict(
        category="Custom Django dashboards, portals & internal tools",
        name="Client portal (files, invoices, status)",
        problem_tags=["no-single-view"],
        setup=(30000, 60000), monthly=(3000, 6000), delivery=(21, 35), skills=CAT7,
    ),
    dict(
        category="Custom Django dashboards, portals & internal tools",
        name="Ops dashboard (single live view of the business)",
        problem_tags=["no-single-view"],
        setup=(25000, 50000), monthly=(2000, 4000), delivery=(21, 28), skills=CAT7,
    ),
    dict(
        category="Custom Django dashboards, portals & internal tools",
        name="Internal tool / approval workflow (custom)",
        problem_tags=["approvals-manual"], custom_quote=True,
        setup=(30000, 80000), monthly=None, delivery=(21, 42), skills=CAT7,
    ),
    # --- 8. Personal productivity ops ---
    dict(
        category="Personal productivity ops",
        name="Calendar & reminder system (n8n + Google Calendar)",
        problem_tags=["mental-load"],
        setup=(6000, 9000), monthly=(1000, 2000), delivery=(7, 7), skills=CAT8,
    ),
    dict(
        category="Personal productivity ops",
        name="Task & document hub (structured Drive/Notion)",
        problem_tags=["scattered-files"],
        setup=(4000, 7000), monthly=(1000, 2000), delivery=(7, 7), skills=CAT8,
    ),
    dict(
        category="Personal productivity ops",
        name="Self-service booking link + confirmations",
        problem_tags=["scheduling-friction"],
        setup=(3000, 5000), monthly=(1000, 1000), delivery=(7, 7), skills=CAT8,
    ),
    dict(
        category="Personal productivity ops",
        name="Personal assistant service (staffing)",
        problem_tags=["personal-chaos"], custom_quote=True,
        setup=None, monthly=None, delivery=(0, 0), skills=CAT8,
    ),
]


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

        created = 0
        for row in SERVICES:
            exists = Service.objects.filter(
                owner=owner, category=row["category"], name=row["name"]
            ).exists()
            if exists:
                continue  # edit-safe: existing rows are never touched
            service = Service(
                owner=owner,
                category=row["category"],
                name=row["name"],
                **self._service_defaults(row),
            )
            service.full_clean()  # clean before save (styleguide); guards transcription
            service.save()
            for skill, min_level in row["skills"]:
                RequiredSkill.objects.get_or_create(
                    service=service, skill=skill, defaults={"min_level": min_level}
                )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog seed for '{owner.username}': {created} created, "
                f"{len(SERVICES) - created} already present (edits preserved)."
            )
        )

    @staticmethod
    def _service_defaults(row: dict[str, Any]) -> dict[str, Any]:
        setup = row.get("setup")
        monthly = row.get("monthly")
        delivery = row.get("delivery")
        return {
            "problem_tags": row.get("problem_tags", []),
            "setup_low": D(setup[0]) if setup else None,
            "setup_high": D(setup[1]) if setup else None,
            "monthly_low": D(monthly[0]) if monthly else None,
            "monthly_high": D(monthly[1]) if monthly else None,
            "custom_quote": bool(row.get("custom_quote")),
            "delivery_days_min": delivery[0] if delivery else None,
            "delivery_days_max": delivery[1] if delivery else None,
        }
