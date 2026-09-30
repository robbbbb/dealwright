"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path("", core_views.home, name="home"),
    path("admin/", admin.site.urls),
    # Auth mockup frame 3: "Resend confirmation" (must precede the allauth include).
    path(
        "accounts/resend-confirmation/",
        core_views.resend_confirmation,
        name="resend_confirmation",
    ),
    path("accounts/", include("allauth.urls")),
    # Card 4: provider skills + team roster ("My skills & team" nav item).
    path("team/", include("team.urls")),
    path("catalog/", include("catalog.urls")),
]
