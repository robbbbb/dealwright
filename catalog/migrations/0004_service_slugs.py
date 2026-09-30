"""Slugs for addressable URLs — services (unique per owner) and required skills
(unique per service). Backfilled once from names; slugs are frozen at creation
so renames never break links. Sequential pks stop being addressable (Robb,
2026-09-30: predictable int URLs are an enumeration surface)."""

from django.db import migrations, models
from django.utils.text import slugify


def _dedupe(queryset, base, exclude_pk):
    candidate, counter = base, 1
    while queryset.filter(slug=candidate).exclude(pk=exclude_pk).exists():
        counter += 1
        candidate = f"{base}-{counter}"
    return candidate


def backfill_slugs(apps, schema_editor):
    Service = apps.get_model("catalog", "Service")
    RequiredSkill = apps.get_model("catalog", "RequiredSkill")
    for service in Service.objects.all():
        service.slug = _dedupe(
            Service.objects.filter(owner_id=service.owner_id),
            slugify(service.name) or "service",
            service.pk,
        )
        service.save(update_fields=["slug"])
    for rs in RequiredSkill.objects.select_related("skill", "service").all():
        rs.slug = _dedupe(
            RequiredSkill.objects.filter(service_id=rs.service_id),
            slugify(rs.skill.name) or "skill",
            rs.pk,
        )
        rs.save(update_fields=["slug"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_skill_not_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="requiredskill",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the skill name, unique per service.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the service name, unique per owner.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
        migrations.RunPython(backfill_slugs, noop_reverse),
        migrations.AddConstraint(
            model_name="service",
            constraint=models.UniqueConstraint(
                fields=["owner", "slug"], name="dw_service_slug_unique_per_owner"
            ),
        ),
        migrations.AddConstraint(
            model_name="requiredskill",
            constraint=models.UniqueConstraint(
                fields=["service", "slug"], name="dw_reqskill_slug_unique_per_service"
            ),
        ),
    ]
