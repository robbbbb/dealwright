"""Catalog admin — CRUD is admin-covered in MVP (design-log build decisions)."""

from __future__ import annotations

from django.contrib import admin

from catalog.models import RequiredSkill, Service, ServiceCategory


class RequiredSkillInline(admin.TabularInline):
    model = RequiredSkill
    extra = 0


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "owner__username", "owner__email")
    autocomplete_fields = ["owner"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name", "category", "owner", "price_summary",
        "delivery_days_min", "delivery_days_max",
    )
    list_filter = ("category",)
    search_fields = ("name", "category__name", "problem_tags")
    inlines = [RequiredSkillInline]
    autocomplete_fields = ["owner"]

