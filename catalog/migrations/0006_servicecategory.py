"""Service categories become a provider-owned registry model (Robb, 2026-10-01).

Supersedes the Service CharField category: categories are picked, not retyped.
Same registry pattern as team.Skill — owner-scoped, slug unique per owner and
frozen at creation, PROTECTed from deletion while referenced by services.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalog", "0005_service_slug_not_null"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, verbose_name="name")),
                ("slug", models.SlugField(blank=True, help_text="URL name — set at creation from the name, unique per owner.", max_length=140, verbose_name="slug")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="service_categories", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "service category",
                "verbose_name_plural": "service categories",
                "ordering": ["name"],
            },
        ),
        migrations.AddConstraint(
            model_name="servicecategory",
            constraint=models.UniqueConstraint(
                fields=("owner", "name"), name="dw_servicecategory_unique_per_owner"
            ),
        ),
        migrations.AddConstraint(
            model_name="servicecategory",
            constraint=models.UniqueConstraint(
                fields=("owner", "slug"), name="dw_servicecategory_slug_unique_per_owner"
            ),
        ),
    ]
