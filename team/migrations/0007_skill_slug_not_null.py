"""Skill slugs become NOT NULL in their own migration (backfill ran in 0006)."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0006_skill_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="skill",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the skill name, unique per owner.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
    ]
