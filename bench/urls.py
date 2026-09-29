"""bench namespace — template references become {% url 'bench:...' %}."""

from django.urls import path

from . import views

app_name = "bench"

urlpatterns = [
    path("", views.bench_home, name="bench_home"),
    path("add/", views.va_add, name="va_add"),
    path("<int:pk>/", views.va_detail, name="va_detail"),
    path("<int:pk>/skills/add/", views.va_skill_add, name="va_skill_add"),
    path("skills/<int:cap_pk>/update/", views.skill_update, name="skill_update"),
    path("skills/<int:cap_pk>/delete/", views.skill_delete, name="skill_delete"),
]
