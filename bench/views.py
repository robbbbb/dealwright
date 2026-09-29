"""Bench & skills views — thin: parse request → validate with form → service → render."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import selectors, services
from .forms import SkillForm, VAForm


@login_required
def bench_home(request: HttpRequest) -> HttpResponse:
    """/bench/ — my skills (solo side) + the bench roster."""
    profile = services.get_provider_profile(request.user)
    skill_form = SkillForm()
    if request.method == "POST":  # add one of my skills
        skill_form = SkillForm(request.POST)
        if skill_form.is_valid():
            services.add_capability(holder=profile, **skill_form.cleaned_data)
            messages.success(request, "Skill added.")
            return redirect("bench:bench_home")
    return render(
        request,
        "bench/bench.html",
        {
            "profile": profile,
            "my_skills": selectors.list_holder_capabilities(profile),
            "skill_form": skill_form,
            "vas": selectors.list_vas(request.user),
            "va_form": VAForm(),
        },
    )


@login_required
def va_add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = VAForm(request.POST)
        if form.is_valid():
            va = services.create_va_profile(owner=request.user, **form.cleaned_data)
            messages.success(request, f"{va.display_name} added to your bench.")
            return redirect("bench:va_detail", pk=va.pk)
    else:
        form = VAForm()
    return render(request, "bench/va_add.html", {"form": form})


@login_required
def va_detail(request: HttpRequest, pk: int) -> HttpResponse:
    va = selectors.get_va_for_owner(request.user, pk)
    if va is None:
        raise Http404("No such bench member.")
    if request.method == "POST":  # edit the VA's own fields
        form = VAForm(request.POST, instance=va)
        if form.is_valid():
            services.update_va_profile(va=va, **form.cleaned_data)
            messages.success(request, "Bench member updated.")
            return redirect("bench:va_detail", pk=va.pk)
    else:
        form = VAForm(instance=va)
    return render(
        request,
        "bench/va_detail.html",
        {
            "va": va,
            "form": form,
            "skills": selectors.list_holder_capabilities(va),
            "skill_form": SkillForm(),
        },
    )


@login_required
@require_POST  # mutations are never GET-reachable (CSRF surface — review pass 1)
def va_skill_add(request: HttpRequest, pk: int) -> HttpResponse:
    va = selectors.get_va_for_owner(request.user, pk)
    if va is None:
        raise Http404("No such bench member.")
    form = SkillForm(request.POST)
    if form.is_valid():
        services.add_capability(holder=va, **form.cleaned_data)
        messages.success(request, f"Skill added to {va.display_name}.")
    else:
        messages.error(request, _first_error(form))
    return redirect("bench:va_detail", pk=va.pk)


def _redirect_target_for(capability) -> HttpResponse:  # type: ignore[no-untyped-def]
    if capability.va_profile_id is not None:
        return redirect("bench:va_detail", pk=capability.va_profile_id)
    return redirect("bench:bench_home")


@login_required
@require_POST  # mutations are never GET-reachable (CSRF surface — review pass 1)
def skill_update(request: HttpRequest, cap_pk: int) -> HttpResponse:
    cap = selectors.get_capability_for_owner(request.user, cap_pk)
    if cap is None:
        raise Http404("No such skill.")
    form = SkillForm(request.POST)
    if form.is_valid():
        services.update_capability(capability=cap, **form.cleaned_data)
        messages.success(request, "Skill updated.")
    else:
        messages.error(request, _first_error(form))
    return _redirect_target_for(cap)


@login_required
@require_POST  # mutations are never GET-reachable (CSRF surface — review pass 1)
def skill_delete(request: HttpRequest, cap_pk: int) -> HttpResponse:
    cap = selectors.get_capability_for_owner(request.user, cap_pk)
    if cap is None:
        raise Http404("No such skill.")
    services.delete_capability(capability=cap)
    messages.success(request, "Skill removed.")
    return _redirect_target_for(cap)


def _first_error(form: SkillForm) -> str:
    """Compact one-line summary for flash-message error display."""
    parts = [f"{field}: {' '.join(errors)}" for field, errors in form.errors.items()]
    return "Please fix the skill form — " + "; ".join(parts)
