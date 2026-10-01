"""team namespace — template references become {% url 'team:...' %}.

Addressable routes use slugs (member slug; capability and registry-skill slugs
unique per owner) — never sequential pks (Robb, 2026-09-30).
"""

from django.urls import path

from . import views

app_name = "team"

urlpatterns = [
    path("", views.team_home, name="team_home"),
    path("add/", views.member_add, name="member_add"),
    path("members/", views.member_list, name="member_list"),  # must precede <slug:member>/
    path("skills/create/", views.skill_create, name="skill_create"),
    path("skills/<slug:skill>/remove/", views.skill_registry_delete, name="skill_registry_delete"),
    # literal route — must precede <slug:member>/
    path("settings/", views.provider_settings, name="provider_settings"),
    path("<slug:member>/", views.member_detail, name="member_detail"),
    path("<slug:member>/engagement/", views.member_engagement, name="member_engagement"),
    path("<slug:member>/skills/add/", views.member_skill_add, name="member_skill_add"),
    path("skills/<slug:cap>/update/", views.skill_update, name="skill_update"),
    path("skills/<slug:cap>/delete/", views.skill_delete, name="skill_delete"),
]
