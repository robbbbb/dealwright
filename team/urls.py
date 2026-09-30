"""team namespace — template references become {% url 'team:...' %}.

Addressable routes use slugs (member slug; capability slug unique per owner) —
never sequential pks (Robb, 2026-09-30, same decision as catalog slugs).
"""

from django.urls import path

from . import views

app_name = "team"

urlpatterns = [
    path("", views.team_home, name="team_home"),
    path("add/", views.member_add, name="member_add"),
    path("<slug:member>/", views.member_detail, name="member_detail"),
    path("<slug:member>/engagement/", views.member_engagement, name="member_engagement"),
    path("<slug:member>/skills/add/", views.member_skill_add, name="member_skill_add"),
    path("skills/<slug:cap>/update/", views.skill_update, name="skill_update"),
    path("skills/<slug:cap>/delete/", views.skill_delete, name="skill_delete"),
]
