"""Team & skills views — thin: parse request → validate with form → service → render."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import selectors, services
from .forms import EngagementForm, SkillForm, SkillPickForm, TeamMemberForm


@login_required
def team_home(request: HttpRequest) -> HttpResponse:
    """/team/ — my skills (solo side) + the team roster."""
    profile = services.get_provider_profile(request.user)
    skill_form = SkillForm()
    if request.method == "POST":  # add one of my skills
        skill_form = SkillForm(request.POST)
        if skill_form.is_valid():
            skill = services.get_or_create_skill(
                owner=request.user, name=skill_form.cleaned_data["skill"]
            )
            services.add_capability(
                holder=profile,
                skill=skill,
                level=skill_form.cleaned_data["level"],
                tasks=skill_form.cleaned_data["tasks"],
            )
            messages.success(request, "Skill added.")
            return redirect("team:team_home")
    return render(
        request,
        "team/team.html",
        {
            "profile": profile,
            "my_skills": selectors.list_holder_capabilities(profile),
            "skill_form": skill_form,
            "vas": selectors.list_vas(request.user),
            "member_form": TeamMemberForm(),
        },
    )


@login_required
def member_add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            va = services.create_va_profile(owner=request.user, **form.cleaned_data)
            messages.success(request, f"{va.display_name} added to your team.")
            return redirect("team:member_detail", member=va.slug)
    else:
        form = TeamMemberForm()
    return render(request, "team/member_add.html", {"form": form})


@login_required
def member_detail(request: HttpRequest, member: str) -> HttpResponse:
    va = selectors.get_va_for_owner(request.user, member)
    if va is None:
        raise Http404("No such team member.")
    if request.method == "POST":  # identity fields
        form = TeamMemberForm(request.POST, instance=va)
        if form.is_valid():
            services.update_va_profile(va=va, **form.cleaned_data)
            messages.success(request, "Team member updated.")
            return redirect("team:member_detail", member=va.slug)
    else:
        form = TeamMemberForm(instance=va)
    return render(
        request,
        "team/member_detail.html",
        {
            "va": va,
            "form": form,
            "engagement_form": EngagementForm(instance=va),
            "skills": selectors.list_holder_capabilities(va),
            "skill_form": SkillPickForm(request.user),
        },
    )


@login_required
@require_POST  # hardening per review: never rely on form validation to reject GET
def member_engagement(request: HttpRequest, member: str) -> HttpResponse:
    """Rates & availability card — the Card 5 hard-filter inputs."""
    va = selectors.get_va_for_owner(request.user, member)
    if va is None:
        raise Http404("No such team member.")
    form = EngagementForm(request.POST, instance=va)
    if form.is_valid():
        services.update_va_profile(va=va, **form.cleaned_data)
        messages.success(request, "Rates & availability saved.")
    else:
        messages.error(request, "Please fix the engagement form.")
    return redirect("team:member_detail", member=va.slug)


@login_required
@require_POST  # mutations are never GET-reachable (CSRF surface — review pass 1)
def member_skill_add(request: HttpRequest, member: str) -> HttpResponse:
    va = selectors.get_va_for_owner(request.user, member)
    if va is None:
        raise Http404("No such team member.")
    form = SkillPickForm(request.user, request.POST)
    if form.is_valid():
        services.add_capability(holder=va, **form.cleaned_data)
        messages.success(request, f"Skill added to {va.display_name}.")
    else:
        messages.error(request, _first_error(form))
    return redirect("team:member_detail", member=va.slug)


def _redirect_target_for(capability) -> HttpResponse:  # type: ignore[no-untyped-def]
    if capability.va_profile_id is not None:
        return redirect("team:member_detail", member=capability.va_profile.slug)
    return redirect("team:team_home")


@login_required
@require_POST  # mutations are never GET-reachable (CSRF surface — review pass 1)
def skill_update(request: HttpRequest, cap: str) -> HttpResponse:
    capability = selectors.get_capability_for_owner(request.user, cap)
    if capability is None:
        raise Http404("No such skill.")
    if cap is None:
        raise Http404("No such skill.")
    form = SkillPickForm(request.user, request.POST)
    if form.is_valid():
        services.update_capability(capability=capability, **form.cleaned_data)
        messages.success(request, "Skill updated.")
    else:
        messages.error(request, _first_error(form))
    return _redirect_target_for(capability)


@login_required
@require_POST  # mutations are never GET-reachable (CSRF surface — review pass 1)
def skill_delete(request: HttpRequest, cap: str) -> HttpResponse:
    capability = selectors.get_capability_for_owner(request.user, cap)
    if capability is None:
        raise Http404("No such skill.")
    if cap is None:
        raise Http404("No such skill.")
    services.delete_capability(capability=capability)
    messages.success(request, "Skill removed.")
    return _redirect_target_for(capability)


def _first_error(form: SkillForm) -> str:
    """Compact one-line summary for flash-message error display."""
    parts = [f"{field}: {' '.join(errors)}" for field, errors in form.errors.items()]
    return "Please fix the skill form — " + "; ".join(parts)
