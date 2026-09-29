"""team namespace — template references become {% url 'team:...' %}."""

from django.urls import path

from . import views

app_name = "team"

urlpatterns = [
    path("", views.team_home, name="team_home"),
    path("add/", views.member_add, name="member_add"),
    path("<int:pk>/", views.member_detail, name="member_detail"),
    path("<int:pk>/skills/add/", views.member_skill_add, name="member_skill_add"),
    path("skills/<int:cap_pk>/update/", views.skill_update, name="skill_update"),
    path("skills/<int:cap_pk>/delete/", views.skill_delete, name="skill_delete"),
]
