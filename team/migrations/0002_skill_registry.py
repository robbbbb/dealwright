"""Skill registry — provider-owned skill names shared by team + catalog (FK joins).

Data-preserving: existing Capability/RequiredSkill strings become Skill rows,
one per (owner, name); the old text columns are dropped after backfill.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_skill_registry(apps, schema_editor):
    Capability = apps.get_model("team", "Capability")
    Skill = apps.get_model("team", "Skill")
    for cap in Capability.objects.select_related("provider_profile__owner", "va_profile__owner"):
        holder_owner = (
            cap.provider_profile.owner if cap.provider_profile_id else cap.va_profile.owner
        )
        skill, _ = Skill.objects.get_or_create(owner=holder_owner, name=cap.skill)
        cap.skill_ref = skill
        cap.save(update_fields=["skill_ref"])


def noop_reverse(apps, schema_editor):
    pass  # structural ops are reversible; the registry rows simply remain


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="name")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skills",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
            ],
            options={
                "verbose_name": "skill",
                "verbose_name_plural": "skills",
                "ordering": ["name"],
            },
        ),
        migrations.AddConstraint(
            model_name="skill",
            constraint=models.UniqueConstraint(
                fields=["owner", "name"], name="dw_skill_unique_per_owner"
            ),
        ),
        migrations.AddField(
            model_name="capability",
            name="skill_ref",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="capabilities",
                to="team.skill",
                verbose_name="skill",
            ),
        ),
        migrations.RunPython(backfill_skill_registry, noop_reverse),
        # Constraints reference `skill` — must drop before the column swap
        # (SQLite remakes the table on RemoveField) and re-add after rename.
        migrations.RemoveConstraint(model_name="capability", name="dw_cap_skill_unique_per_provider"),
        migrations.RemoveConstraint(model_name="capability", name="dw_cap_skill_unique_per_va"),
        migrations.RemoveField(model_name="capability", name="skill"),
        migrations.RenameField(model_name="capability", old_name="skill_ref", new_name="skill"),
        migrations.AddConstraint(
            model_name="capability",
            constraint=models.UniqueConstraint(
                fields=["provider_profile", "skill"],
                condition=models.Q(provider_profile__isnull=False),
                name="dw_cap_skill_unique_per_provider",
            ),
        ),
        migrations.AddConstraint(
            model_name="capability",
            constraint=models.UniqueConstraint(
                fields=["va_profile", "skill"],
                condition=models.Q(va_profile__isnull=False),
                name="dw_cap_skill_unique_per_va",
            ),
        ),
    ]

