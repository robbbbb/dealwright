"""catalog namespace — template references become {% url 'catalog:...' %}.

Addressable routes use slugs (category + service, category + service + skill) —
never sequential pks (Robb, 2026-09-30: predictable int URLs are an
enumeration surface). The service slug is unique per owner; the category slug
is validated against the record so URLs stay canonical.
"""

from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.service_list, name="service_list"),
    path("seed/", views.seed_defaults, name="seed_defaults"),
    path("add/", views.service_create, name="service_create"),
    path("categories/add/", views.category_add, name="category_add"),  # precedes <slug:category>/…
    path("<slug:category>/<slug:service>/", views.service_edit, name="service_edit"),
    path("<slug:category>/<slug:service>/delete/", views.service_delete, name="service_delete"),
    path(
        "<slug:category>/<slug:service>/skills/add/",
        views.skill_add,
        name="skill_add",
    ),
    path(
        "<slug:category>/<slug:service>/skills/<slug:skill>/delete/",
        views.skill_delete,
        name="skill_delete",
    ),
]
