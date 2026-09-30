"""Slugs for team URLs — VAProfile (unique per owner) and Capability (unique per
owner across holders). Backfilled once from names; frozen at creation so
renames never break links. Sequential pks stop being addressable (Robb,
2026-09-30 — same decision as catalog slugs)."""

from django.db import migrations, models
from django.utils.text import slugify


def _dedupe(queryset, base, exclude_pk):
    candidate, counter = base, 1
    while queryset.filter(slug=candidate).exclude(pk=exclude_pk).exists():
        counter += 1
        candidate = f"{base}-{counter}"
    return candidate


def backfill_slugs(apps, schema_editor):
    VAProfile = apps.get_model("team", "VAProfile")
    Capability = apps.get_model("team", "Capability")
    for va in VAProfile.objects.all():
        va.slug = _dedupe(
            VAProfile.objects.filter(owner_id=va.owner_id),
            slugify(va.display_name) or "member",
            va.pk,
        )
        va.save(update_fields=["slug"])
    for cap in Capability.objects.select_related("skill", "provider_profile__owner", "va_profile__owner"):
        holder_owner = (
            cap.provider_profile.owner if cap.provider_profile_id else cap.va_profile.owner
        )
        cap.slug = _dedupe(
            Capability.objects.filter(
                models.Q(provider_profile__owner_id=holder_owner.pk)
                | models.Q(va_profile__owner_id=holder_owner.pk)
            ),
            slugify(cap.skill.name) or "skill",
            cap.pk,
        )
        cap.save(update_fields=["slug"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0003_capability_skill_not_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="capability",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the skill name, unique per owner.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
        migrations.AddField(
            model_name="vaprofile",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the display name, unique per owner.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
        migrations.RunPython(backfill_slugs, noop_reverse),
        migrations.AddConstraint(
            model_name="capability",
            constraint=models.UniqueConstraint(
                condition=models.Q(provider_profile__isnull=False),
                fields=["provider_profile", "slug"],
                name="dw_cap_slug_unique_per_provider",
            ),
        ),
        migrations.AddConstraint(
            model_name="capability",
            constraint=models.UniqueConstraint(
                condition=models.Q(va_profile__isnull=False),
                fields=["va_profile", "slug"],
                name="dw_cap_slug_unique_per_va",
            ),
        ),
        migrations.AddConstraint(
            model_name="vaprofile",
            constraint=models.UniqueConstraint(
                fields=["owner", "slug"], name="dw_va_slug_unique_per_owner"
            ),
        ),
    ]
