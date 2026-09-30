"""Team slugs become NOT NULL in their own migration (backfill ran in 0004)."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0004_team_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="capability",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the skill name, unique per owner.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
        migrations.AlterField(
            model_name="vaprofile",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL name — set at creation from the display name, unique per owner.",
                max_length=140,
                verbose_name="slug",
            ),
        ),
    ]
