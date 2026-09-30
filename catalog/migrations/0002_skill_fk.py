"""RequiredSkill.skill becomes a registry FK (team.Skill) — exact-join matching.

Data-preserving: existing text skill names are backfilled into the owner's
Skill registry (reusing rows created by team's 0002 where names coincide).
"""

from django.db import migrations, models
import django.db.models.deletion


def backfill_required_skills(apps, schema_editor):
    RequiredSkill = apps.get_model("catalog", "RequiredSkill")
    Skill = apps.get_model("team", "Skill")
    for rs in RequiredSkill.objects.select_related("service__owner"):
        skill, _ = Skill.objects.get_or_create(owner=rs.service.owner, name=rs.skill)
        rs.skill_ref = skill
        rs.save(update_fields=["skill_ref"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
        ("team", "0002_skill_registry"),
    ]

    operations = [
        migrations.AddField(
            model_name="requiredskill",
            name="skill_ref",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="required_by",
                to="team.skill",
                verbose_name="skill",
            ),
        ),
        migrations.RunPython(backfill_required_skills, noop_reverse),
        migrations.RemoveConstraint(
            model_name="requiredskill", name="dw_reqskill_unique_per_service"
        ),
        migrations.RemoveField(model_name="requiredskill", name="skill"),
    ]
