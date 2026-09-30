"""Skill registry rows become addressable — slug unique per owner, frozen at
creation (backfilled once from names). Robb, 2026-09-30: expose the skill-list
manager; removal routes need slugs like everything else."""

from django.db import migrations, models
from django.utils.text import slugify


def backfill_slugs(apps, schema_editor):
    Skill = apps.get_model("team", "Skill")
    for skill in Skill.objects.all():
        base, candidate, counter = (slugify(skill.name) or "skill"), (slugify(skill.name) or "skill"), 1
        while (
            Skill.objects.filter(owner_id=skill.owner_id, slug=candidate)
            .exclude(pk=skill.pk)
            .exists()
        ):
            counter += 1
            candidate = f"{base}-{counter}"
        skill.slug = candidate
        skill.save(update_fields=["slug"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0005_team_slugs_not_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="skill",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the skill name, unique per owner.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
        migrations.RunPython(backfill_slugs, noop_reverse),
        migrations.AddConstraint(
            model_name="skill",
            constraint=models.UniqueConstraint(
                fields=["owner", "slug"], name="dw_skill_slug_unique_per_owner"
            ),
        ),
    ]
