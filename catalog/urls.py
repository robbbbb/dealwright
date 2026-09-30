"""catalog namespace — template references become {% url 'catalog:...' %}."""

from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.service_list, name="service_list"),
    path("seed/", views.seed_defaults, name="seed_defaults"),
    path("add/", views.service_create, name="service_create"),
    path("<int:pk>/", views.service_edit, name="service_edit"),
    path("<int:pk>/delete/", views.service_delete, name="service_delete"),
    path("<int:pk>/skills/add/", views.skill_add, name="skill_add"),
    path("skills/<int:skill_pk>/delete/", views.skill_delete, name="skill_delete"),
]
