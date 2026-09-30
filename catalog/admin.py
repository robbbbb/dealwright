"""Catalog admin — CRUD is admin-covered in MVP (design-log build decisions)."""

from __future__ import annotations

from django.contrib import admin

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

