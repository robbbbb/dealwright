"""Backfill: one ServiceCategory row per distinct (owner, category) string,
then repoint every service at its row. Data-preserving — no string values are
dropped; slugs are deduped per owner exactly like the model's save() does.
"""

from django.db import migrations
from django.utils.text import slugify


def _unique_slug(ServiceCategory, owner_id: int, base: str) -> str:
    candidate, counter = base, 1
    while ServiceCategory.objects.filter(owner_id=owner_id, slug=candidate).exists():
        counter += 1
        candidate = f"{base}-{counter}"
    return candidate


def backfill_categories(apps, schema_editor):
    Service = apps.get_model("catalog", "Service")
    ServiceCategory = apps.get_model("catalog", "ServiceCategory")
    seen: dict[tuple[int, str], int] = {}
    for service in Service.objects.all().order_by("pk").iterator():
        key = (service.owner_id, service.category)
        if key not in seen:
            category, _ = ServiceCategory.objects.get_or_create(
                owner_id=service.owner_id, name=service.category
            )
            if not category.slug:
                category.slug = _unique_slug(
                    ServiceCategory, service.owner_id, slugify(service.category) or "category"
                )
                category.save(update_fields=["slug"])
            seen[key] = category.pk
    for service in Service.objects.filter(category_fk__isnull=True).iterator():
        service.category_fk_id = seen[(service.owner_id, service.category)]
        service.save(update_fields=["category_fk"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_service_category_fk"),
    ]

    operations = [
        migrations.RunPython(backfill_categories, noop_reverse),
    ]
