"""Catalog views — thin: parse request → validate with form → service → render."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import selectors, services
from .forms import RequiredSkillForm, ServiceForm


@login_required
def service_list(request: HttpRequest) -> HttpResponse:
    """/catalog/ — the provider's services grouped by category."""
    services_qs = selectors.list_services(request.user)
    categories = {}
    for service in services_qs:
        categories.setdefault(service.category, []).append(service)
    return render(
        request,
        "catalog/service_list.html",
        {
            "categories": sorted(categories.items()),
            "service_count": services_qs.count(),
        },
    )


@login_required
@require_POST
def seed_defaults(request: HttpRequest) -> HttpResponse:
    """Load the default catalog (25 services) — only creates missing rows."""
    created, total = services.seed_default_catalog(owner=request.user)
    if created:
        messages.success(request, f"Loaded {created} default services (edits preserved).")
    else:
        messages.info(request, f"All {total} default services were already in your catalog.")
    return redirect("catalog:service_list")


@login_required
def service_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            fields = {k: v for k, v in form.cleaned_data.items() if k != "tags_text"}
            service = services.create_service(owner=request.user, **fields)
            messages.success(request, f"{service.name} added to your catalog.")
            return redirect("catalog:service_edit", pk=service.pk)
    else:
        form = ServiceForm()
    return render(request, "catalog/service_form.html", {"form": form, "is_create": True})


@login_required
def service_edit(request: HttpRequest, pk: int) -> HttpResponse:
    service = selectors.get_service_for_owner(request.user, pk)
    if service is None:
        raise Http404("No such service.")
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            fields = {k: v for k, v in form.cleaned_data.items() if k != "tags_text"}
            services.update_service(service=service, **fields)
            messages.success(request, "Service updated.")
            return redirect("catalog:service_edit", pk=service.pk)
    else:
        form = ServiceForm(instance=service)
    return render(
        request,
        "catalog/service_form.html",
        {
            "form": form,
            "is_create": False,
            "service": service,
            "required_skills": service.required_skills.all(),
            "skill_form": RequiredSkillForm(),
        },
    )


@login_required
@require_POST
def service_delete(request: HttpRequest, pk: int) -> HttpResponse:
    service = selectors.get_service_for_owner(request.user, pk)
    if service is None:
        raise Http404("No such service.")
    services.delete_service(service=service)
    messages.success(request, f"{service.name} removed from your catalog.")
    return redirect("catalog:service_list")


@login_required
@require_POST
def skill_add(request: HttpRequest, pk: int) -> HttpResponse:
    service = selectors.get_service_for_owner(request.user, pk)
    if service is None:
        raise Http404("No such service.")
    form = RequiredSkillForm(request.POST)
    if form.is_valid():
        services.add_required_skill(
            service=service,
            skill=form.cleaned_data["skill"],
            min_level=form.cleaned_data["min_level"],
        )
        messages.success(request, "Required skill added.")
    else:
        messages.error(request, "Please add a skill name and level.")
    return redirect("catalog:service_edit", pk=service.pk)


@login_required
@require_POST
def skill_delete(request: HttpRequest, skill_pk: int) -> HttpResponse:
    required = selectors.get_required_skill_for_owner(request.user, skill_pk)
    if required is None:
        raise Http404("No such required skill.")
    service_pk = required.service_id
    services.delete_required_skill(required=required)
    messages.success(request, "Required skill removed.")
    return redirect("catalog:service_edit", pk=service_pk)
