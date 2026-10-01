"""Stage 1 of the CharField → FK category swap: nullable FK column to backfill."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0006_servicecategory"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="category_fk",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="catalog.servicecategory",
            ),
        ),
    ]
