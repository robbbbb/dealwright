"""Slugs become NOT NULL in their own migration (backfill ran in 0004)."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_service_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the service name, unique per owner.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
        migrations.AlterField(
            model_name="requiredskill",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the skill name, unique per service.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
    ]
