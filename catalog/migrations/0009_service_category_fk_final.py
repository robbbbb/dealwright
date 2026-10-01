"""Stage 2 of the category swap: drop the CharField, rename the backfilled FK
column to `category`, make it NOT NULL (0008 backfilled every row), and rebuild
the per-owner unique constraint on the new column. In-use categories are
PROTECTed from deletion by the final field definition.

Order note: the unique constraint is dropped FIRST — SQLite rebuilds the table
column-by-column, and a constraint referencing a removed field breaks the
rebuild. It is re-added last, on the final schema.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_backfill_category_fk"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="service",
            name="dw_service_unique_per_owner",  # drop before the column leaves (SQLite table rebuilds)
        ),
        migrations.RemoveField(model_name="service", name="category"),
        migrations.RenameField(
            model_name="service", old_name="category_fk", new_name="category"
        ),
        migrations.AlterField(
            model_name="service",
            name="category",
            field=models.ForeignKey(
                help_text="Pick from the provider's own category rows (supersedes free text, 2026-10-01).",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="services",
                to="catalog.servicecategory",
                verbose_name="category",
            ),
        ),
        migrations.AddConstraint(
            model_name="service",
            constraint=models.UniqueConstraint(
                fields=("owner", "category", "name"),
                name="dw_service_unique_per_owner",
            ),
        ),
    ]
