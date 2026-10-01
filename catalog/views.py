"""Catalog views — thin: parse request → validate with form → service → render."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from . import selectors, services
from .forms import CategoryForm, RequiredSkillForm, ServiceForm


@login_required
def service_list(request: HttpRequest) -> HttpResponse:
    """/catalog/ — the provider's services grouped by category."""
    services_qs = selectors.list_services(request.user)
    categories: dict[str, list] = {}
    for service in services_qs:
        categories.setdefault(service.category.name, []).append(service)
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
def category_add(request: HttpRequest) -> HttpResponse:
    """Add a category row — the vocabulary services are picked from."""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category, created = services.get_or_create_category(
                owner=request.user, name=form.cleaned_data["name"]
            )
            if created:
                messages.success(request, f"'{category.name}' added to your categories.")
            else:
                messages.info(request, f"'{category.name}' is already in your categories.")
            return redirect("catalog:service_list")
    else:
        form = CategoryForm()
    return render(request, "catalog/category_add.html", {"form": form})


@login_required
def service_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ServiceForm(request.user, request.POST)
        if form.is_valid():
            fields = {k: v for k, v in form.cleaned_data.items() if k != "tags_text"}
            service = services.create_service(owner=request.user, **fields)
            messages.success(request, f"{service.name} added to your catalog.")
            return redirect(
                "catalog:service_edit",
                category=slugify(service.category.name),
                service=service.slug,
            )
    else:
        form = ServiceForm(request.user)
    return render(
        request,
        "catalog/service_form.html",
        {"form": form, "is_create": True, "categories": selectors.list_categories(request.user)},
    )


def _canonical_service(request: HttpRequest, category: str, service_slug: str):
    """Slug lookup + tenancy + canonical category — anything else is a 404."""
    service = selectors.get_service_for_owner(request.user, service_slug)
    if service is None or slugify(service.category.name) != category:
        raise Http404("No such service.")
    return service


@login_required
def service_edit(request: HttpRequest, category: str, service: str) -> HttpResponse:
    svc = _canonical_service(request, category, service)
    if request.method == "POST":
        form = ServiceForm(request.user, request.POST, instance=svc)
        if form.is_valid():
            fields = {k: v for k, v in form.cleaned_data.items() if k != "tags_text"}
            services.update_service(service=svc, **fields)
            messages.success(request, "Service updated.")
            return redirect(
                "catalog:service_edit",
                category=slugify(svc.category),
                service=svc.slug,
            )
    else:
        form = ServiceForm(request.user, instance=svc)
    return render(
        request,
        "catalog/service_form.html",
        {
            "form": form,
            "is_create": False,
            "service": svc,
            "required_skills": svc.required_skills.select_related("skill"),
            "skill_form": RequiredSkillForm(request.user),
        },
    )


@login_required
@require_POST
def service_delete(request: HttpRequest, category: str, service: str) -> HttpResponse:
    svc = _canonical_service(request, category, service)
    services.delete_service(service=svc)
    messages.success(request, f"{svc.name} removed from your catalog.")
    return redirect("catalog:service_list")


@login_required
@require_POST
def skill_add(request: HttpRequest, category: str, service: str) -> HttpResponse:
    svc = _canonical_service(request, category, service)
    form = RequiredSkillForm(request.user, request.POST)
    if form.is_valid():
        services.add_required_skill(
            service=svc,
            skill=form.cleaned_data["skill"],
            min_level=form.cleaned_data["min_level"],
        )
        messages.success(request, "Required skill added.")
    else:
        messages.error(request, "Please add a skill name and level.")
    return _redirect_to_service(svc)


def _redirect_to_service(svc) -> HttpResponse:  # type: ignore[no-untyped-def]
    return redirect(
        "catalog:service_edit", category=slugify(svc.category.name), service=svc.slug
    )


@login_required
@require_POST
def skill_delete(
    request: HttpRequest, category: str, service: str, skill: str
) -> HttpResponse:
    svc = _canonical_service(request, category, service)
    required = selectors.get_required_skill_for_service(svc, skill)
    if required is None:
        raise Http404("No such required skill.")
    services.delete_required_skill(required=required)
    messages.success(request, "Required skill removed.")
    return _redirect_to_service(svc)
