"""Catalog admin — CRUD is admin-covered in MVP (design-log build decisions)."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.models import User

from catalog.models import RequiredSkill, Service


class RequiredSkillInline(admin.TabularInline):
    model = RequiredSkill
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name", "category", "owner", "price_summary",
        "delivery_days_min", "delivery_days_max",
    )
    list_filter = ("category",)
    search_fields = ("name", "category", "problem_tags")
    inlines = [RequiredSkillInline]
    autocomplete_fields = ["owner"]

    def get_search_results(self, request, queryset, search_term):
        return super().get_search_results(request, queryset, search_term)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by("username")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
