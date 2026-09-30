"""Rename skill_ref→skill and set NOT NULL in a clean transaction.

Postgres rule (bit us in 0002): an FK-targeting rename/alter cannot run in the
same transaction as inserts into the referenced table (pending trigger events).
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_skill_fk"),
        ("team", "0003_capability_skill_not_null"),
    ]

    operations = [
        migrations.RenameField(
            model_name="requiredskill", old_name="skill_ref", new_name="skill"
        ),
        migrations.AlterField(
            model_name="requiredskill",
            name="skill",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="required_by",
                to="team.skill",
                verbose_name="skill",
            ),
        ),
          migrations.AddConstraint(
            model_name="requiredskill",
            constraint=models.UniqueConstraint(
                fields=["service", "skill"], name="dw_reqskill_unique_per_service"
            ),
        ),
    ]
