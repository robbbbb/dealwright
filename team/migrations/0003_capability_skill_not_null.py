"""Separate transaction for the NOT NULL alter (Postgres pending-trigger rule)."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0002_skill_registry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="capability",
            name="skill",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="capabilities",
                to="team.skill",
                verbose_name="skill",
                help_text="Registry row — exact FK join feeds Card 5 matching.",
            ),
        ),
    ]
