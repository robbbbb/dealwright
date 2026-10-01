"""ROI engine — deterministic money math. No LLM, no DB, no Django.

Pure functions: dataclasses in, dataclasses out. All money is Decimal;
2dp ROUND_HALF_UP rounding happens only at the output edge. Currency is a
passthrough label — never converted (Q3: no FX, ever).

Modes (Q7 — exclusive per estimate line, never blended):
- automation: task-time reduction on a workflow someone runs today
- delegation: reclaimed client/employee time vs VA cost (social/admin VAs)
- qualitative: no computation possible — callers render the reason instead

Estimates are always labelled estimates; every figure traces to a stored
assumption (workflow input, benchmark band, or provider override).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

TWO_DP = Decimal("0.01")
ONE_DP = Decimal("0.1")
WEEKS_PER_MONTH = Decimal("4.33")

SCENARIO_KEYS = ("conservative", "expected", "optimistic")

PERFORMED_BY_CHOICES = ("client", "employee", "nobody", "outsourced")


@dataclass(frozen=True)
class Band:
    """Low/mid/high band (or a point estimate: all three equal)."""

    low: Decimal
    mid: Decimal
    high: Decimal

    def __post_init__(self) -> None:
        for name in ("low", "mid", "high"):
            if not isinstance(getattr(self, name), Decimal):
                raise TypeError(f"Band.{name} must be Decimal")
        if self.low < 0 or self.mid < self.low or self.high < self.mid:
            raise ValueError("Band must satisfy 0 <= low <= mid <= high")

    def scenarios(self) -> dict[str, Decimal]:
        return {"conservative": self.low, "expected": self.mid, "optimistic": self.high}


def band_from(config: dict) -> Band:
    """Build a Band from a config dict ({"low": 40, "mid": 60, "high": 80})."""
    try:
        return Band(*(Decimal(str(config[key])) for key in ("low", "mid", "high")))
    except (KeyError, TypeError, InvalidOperation) as exc:
        raise ValueError(f"Malformed benchmark band: {config!r}") from exc


def band_point(value: Decimal) -> Band:
    """A point estimate as a degenerate band (pastor case: 75% → 75/75/75)."""
    return Band(value, value, value)


@dataclass(frozen=True)
class WorkflowInput:
    """One workflow row (mirrors the planned WorkflowActivity fields).

    performed_by: "client" | "employee" | "nobody" | "outsourced"
    """

    performed_by: str
    hours_per_week: Decimal | None = None
    hourly_cost: Decimal | None = None  # the time value of whoever performs it
    employees: int = 1

    def __post_init__(self) -> None:
        if self.performed_by not in PERFORMED_BY_CHOICES:
            raise ValueError(f"performed_by must be one of {PERFORMED_BY_CHOICES}")
        if self.employees < 0:
            raise ValueError("employees must be >= 0")
        if self.hours_per_week is not None and self.hours_per_week < 0:
            raise ValueError("hours_per_week must be >= 0")
        if self.hourly_cost is not None and self.hourly_cost < 0:
            raise ValueError("hourly_cost must be >= 0")

    @property
    def monthly_hours(self) -> Decimal | None:
        if self.hours_per_week is None:
            return None
        return (self.hours_per_week * WEEKS_PER_MONTH).quantize(TWO_DP, ROUND_HALF_UP)


@dataclass(frozen=True)
class ScenarioLine:
    """One scenario row — hours, value, cost, net, payback."""

    hours: Decimal
    value: Decimal
    cost: Decimal
    net: Decimal
    payback_months: Decimal | None


@dataclass(frozen=True)
class ModeEstimate:
    """The result of one workflow × one mode — three scenario lines."""

    mode: str  # "automation" | "delegation"
    currency: str  # passthrough label (Q3: no FX)
    lines: dict[str, ScenarioLine]  # conservative / expected / optimistic
    band_used: Band  # the band (or point) that produced the scenarios


def _money(value: Decimal) -> Decimal:
    return value.quantize(TWO_DP, ROUND_HALF_UP)


def _hours(value: Decimal) -> Decimal:
    """Hours are reported to a tenth — and money is computed from the REPORTED
    hours, never hidden precision (traceable-figures discipline)."""
    return value.quantize(ONE_DP, ROUND_HALF_UP)


def _payback(setup_low: Decimal | None, net: Decimal) -> Decimal | None:
    """Months to recover setup at the scenario's monthly net.

    None when there is no setup to recover or the net is not positive —
    never a division by zero, never a negative-nonsense figure.
    """
    if setup_low is None or net <= 0:
        return None
    return (setup_low / net).quantize(Decimal("0.1"), ROUND_HALF_UP)


def _validate_common(inp: WorkflowInput) -> None:
    if inp.performed_by == "nobody":
        raise ValueError(
            "No one performs this workflow today — nothing to compute (qualitative only)."
        )
    if inp.hours_per_week is None or inp.hourly_cost is None:
        raise ValueError(
            "Capture hours per week and the performer's time value before computing "
            "(follow-up questions)."
        )


def automation_estimate(
    inp: WorkflowInput,
    reduction: Band,
    *,
    currency: str = "PHP",
    setup_low: Decimal | None = None,
) -> ModeEstimate:
    """Automation mode: monthly_hours × reduction% × time value × employees.

    Labor savings only; revenue gain (leads × value × uplift) is computed
    separately by revenue_gain() and is never folded into these nets.
    """
    _validate_common(inp)
    if inp.employees == 0:
        raise ValueError(
            "employees is 0 — labor savings would be silently zero; fix the workflow row."
        )
    monthly_hours = inp.monthly_hours
    assert monthly_hours is not None  # _validate_common guarantees hours
    lines: dict[str, ScenarioLine] = {}
    for key, pct in reduction.scenarios().items():
        hours_saved = _hours(monthly_hours * pct / Decimal(100))
        value = _money(hours_saved * inp.hourly_cost * inp.employees)  # type: ignore[operator]
        lines[key] = ScenarioLine(
            hours=hours_saved, value=value, cost=Decimal("0.00"),
            net=value, payback_months=_payback(setup_low, value),
        )
    return ModeEstimate(mode="automation", currency=currency, lines=lines, band_used=reduction)


def delegation_estimate(
    inp: WorkflowInput,
    handoff_share: Band,
    va_hourly_rate: Decimal,
    *,
    currency: str = "PHP",
    setup_low: Decimal | None = None,
) -> ModeEstimate:
    """Delegation mode: hours handed off × client's time value − VA cost.

    The social/admin-VA case: the client's reclaimed hours ARE the benefit;
    no reduction percentage is invented. va_hourly_rate is a stored rate
    (bench or retainer converted by the caller) — never estimated here.
    """
    _validate_common(inp)
    if va_hourly_rate < 0:
        raise ValueError("va_hourly_rate must be >= 0")
    monthly_hours = inp.monthly_hours
    assert monthly_hours is not None
    lines: dict[str, ScenarioLine] = {}
    for key, share in handoff_share.scenarios().items():
        hours = _hours(monthly_hours * share / Decimal(100))
        value = _money(hours * inp.hourly_cost)  # type: ignore[operator]
        cost = _money(hours * va_hourly_rate)
        lines[key] = ScenarioLine(
            hours=hours, value=value, cost=cost, net=value - cost,
            payback_months=_payback(setup_low, value - cost),
        )
    return ModeEstimate(mode="delegation", currency=currency, lines=lines, band_used=handoff_share)


def revenue_gain(
    leads_per_month: Decimal,
    value_per_lead: Decimal,
    uplift: Band,
) -> dict[str, Decimal]:
    """Revenue-lever estimate — ONLY for sessions that captured lead data.

    Reported as its own labelled line; never folded into labor net or payback
    (claims discipline: revenue projections stay quarantined).
    """
    if leads_per_month < 0 or value_per_lead < 0:
        raise ValueError("lead inputs must be >= 0")
    return {
        key: _money(leads_per_month * value_per_lead * pct / Decimal(100))
        for key, pct in uplift.scenarios().items()
    }


def select_mode(
    performed_by: str,
    hours_per_week: Decimal | None,
    hourly_cost: Decimal | None,
) -> tuple[str, str]:
    """(mode, reason) — 'qualitative' always carries an explanation.

    The service's benefit profile decides which computed modes are allowed;
    this function decides whether ANY computation is possible from the data.
    """
    if performed_by == "nobody":
        return (
            "qualitative",
            "No one performs this workflow today — there are no hours to reclaim or reduce.",
        )
    if hours_per_week is None or hourly_cost is None:
        return (
            "qualitative",
            "Capture hours per week and the performer's time value to unlock computation "
            "(follow-up questions).",
        )
    return (
        "computed",
        "Workflow data is complete — the service's benefit profile picks automation or delegation.",
    )


def rollup(estimates: list[ModeEstimate]) -> dict[str, Decimal]:
    """Sum net across workflow estimates per scenario (multi-workflow rollup).

    Single-currency by contract: mixing currencies would silently produce
    nonsense — a named "never" in the guardrail language (no FX, no blending).
    """
    currencies = {est.currency for est in estimates}
    if len(currencies) > 1:
        raise ValueError(f"Mixed-currency rollup is not allowed: {sorted(currencies)}")
    totals = {key: Decimal("0.00") for key in SCENARIO_KEYS}
    for est in estimates:
        for key, line in est.lines.items():
            totals[key] += line.net
    return {key: _money(value) for key, value in totals.items()}
