"""ROI engine tests — the 95–100% tier (Card 3).

Worked-example anchors come from the design docs:
- pastor case (build plan Card 3): 12h/mo, 75% reduction, ₱300/hr → 9h, ₱2,700
- LF case (build plan Card 3): 26 / 31.2 / 34.6 hrs → ₱7,280 / 8,736 / 9,688
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.test import override_settings

from core.roi.engine import (
    Band,
    WorkflowInput,
    automation_estimate,
    band_from,
    band_point,
    delegation_estimate,
    revenue_gain,
    rollup,
    select_mode,
)

D = Decimal


# --- band construction ----------------------------------------------------------------


class TestBand:
    def test_from_config_dict(self) -> None:
        band = band_from({"low": 40, "mid": 60, "high": 80})
        assert band == Band(D("40"), D("60"), D("80"))

    def test_malformed_config_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Malformed benchmark band"):
            band_from({"low": 40})

    def test_point_estimate_is_degenerate_band(self) -> None:
        assert band_point(D("75")).scenarios() == {
            "conservative": D("75"), "expected": D("75"), "optimistic": D("75"),
        }

    def test_ordering_enforced(self) -> None:
        with pytest.raises(ValueError, match="0 <= low <= mid <= high"):
            Band(D("80"), D("60"), D("40"))
        with pytest.raises(ValueError, match="0 <= low <= mid <= high"):
            Band(D("-5"), D("0"), D("10"))

    def test_non_decimal_rejected(self) -> None:
        with pytest.raises(TypeError, match="must be Decimal"):
            Band(40, 60, 80)


# --- workflow input -------------------------------------------------------------------


class TestWorkflowInput:
    def test_monthly_hours_uses_433(self) -> None:
        assert WorkflowInput("client", D("8"), D("400")).monthly_hours == D("34.64")

    def test_zero_employees_allowed_at_input_but_rejected_by_modes(self) -> None:
        assert WorkflowInput("client", D("8"), D("400"), employees=0).employees == 0

    def test_negative_values_rejected(self) -> None:
        with pytest.raises(ValueError, match="employees"):
            WorkflowInput("client", D("8"), D("400"), employees=-1)
        with pytest.raises(ValueError, match="hours_per_week"):
            WorkflowInput("client", D("-8"), D("400"))
        with pytest.raises(ValueError, match="hourly_cost"):
            WorkflowInput("client", D("8"), D("-400"))

    def test_unknown_performed_by_rejected(self) -> None:
        with pytest.raises(ValueError, match="performed_by"):
            WorkflowInput("robot", D("8"), D("400"))


# --- TDD anchor 1: pastor case (automation) -------------------------------------------


class TestPastorCase:
    def test_expected_numbers(self) -> None:
        """12h/mo, 75% reduction, ₱300/hr → 9h, ₱2,700 (build-plan anchor)."""
        inp = WorkflowInput("client", hours_per_week=D("12") / D("4.33"), hourly_cost=D("300"))
        est = automation_estimate(inp, band_point(D("75")))
        line = est.lines["expected"]
        assert line.hours == D("9.0")
        assert line.value == D("2700.00")
        assert line.net == D("2700.00")
        assert line.cost == D("0.00")

    def test_band_produces_three_scenarios(self) -> None:
        inp = WorkflowInput("client", hours_per_week=D("12") / D("4.33"), hourly_cost=D("300"))
        est = automation_estimate(inp, Band(D("50"), D("75"), D("80")))
        assert [est.lines[k].hours for k in ("conservative", "expected", "optimistic")] == [
            D("6.0"), D("9.0"), D("9.6"),
        ]

    def test_employees_multiply_labor_value(self) -> None:
        inp = WorkflowInput(
            "employee", hours_per_week=D("12") / D("4.33"), hourly_cost=D("300"), employees=3
        )
        est = automation_estimate(inp, band_point(D("75")))
        assert est.lines["expected"].value == D("8100.00")  # 3 × ₱2,700

    def test_payback_against_setup(self) -> None:
        inp = WorkflowInput("client", hours_per_week=D("12") / D("4.33"), hourly_cost=D("300"))
        est = automation_estimate(inp, band_point(D("75")), setup_low=D("5400"))
        assert est.lines["expected"].payback_months == D("2.0")

    def test_zero_employees_rejected_not_silently_zero(self) -> None:
        inp = WorkflowInput("client", hours_per_week=D("12"), hourly_cost=D("300"), employees=0)
        with pytest.raises(ValueError, match="employees is 0"):
            automation_estimate(inp, band_point(D("75")))


# --- TDD anchor 2: LF case (delegation) ------------------------------------------------


def _lf_input() -> WorkflowInput:
    return WorkflowInput("client", hours_per_week=D("8"), hourly_cost=D("400"))


class TestLFCase:
    def test_scenario_rows_match_design_anchors(self) -> None:
        """8 hrs/wk, handoff 75/90/100%, ₱400 time value, ₱120/hr VA.

        → 26.0 / 31.2 / 34.6 hrs freed → nets ₱7,280 / 8,736 / 9,688.
        """
        est = delegation_estimate(_lf_input(), Band(D("75"), D("90"), D("100")), D("120"))
        hours = [est.lines[k].hours for k in ("conservative", "expected", "optimistic")]
        values = [est.lines[k].value for k in ("conservative", "expected", "optimistic")]
        costs = [est.lines[k].cost for k in ("conservative", "expected", "optimistic")]
        nets = [est.lines[k].net for k in ("conservative", "expected", "optimistic")]
        assert hours == [D("26.0"), D("31.2"), D("34.6")]
        assert values == [D("10400.00"), D("12480.00"), D("13840.00")]
        assert costs == [D("3120.00"), D("3744.00"), D("4152.00")]
        assert nets == [D("7280.00"), D("8736.00"), D("9688.00")]

    def test_payback_vs_setup(self) -> None:
        est = delegation_estimate(
            _lf_input(), Band(D("75"), D("90"), D("100")), D("120"), setup_low=D("6000")
        )
        assert est.lines["expected"].payback_months == D("0.7")  # 6000 / 8736.00

    def test_currency_passthrough(self) -> None:
        est = delegation_estimate(_lf_input(), Band(D("75"), D("90"), D("100")), D("120"))
        assert est.currency == "PHP"

    def test_zero_va_rate_gives_full_value_as_net(self) -> None:
        est = delegation_estimate(_lf_input(), Band(D("100"), D("100"), D("100")), D("0"))
        assert est.lines["expected"].net == est.lines["expected"].value


# --- qualitative + mode selection ------------------------------------------------------


class TestSelectMode:
    def test_nobody_performs_is_qualitative(self) -> None:
        mode, reason = select_mode("nobody", None, None)
        assert mode == "qualitative"
        assert "no hours to reclaim" in reason

    def test_missing_data_is_qualitative_with_followup_reason(self) -> None:
        mode, reason = select_mode("client", None, D("400"))
        assert mode == "qualitative"
        assert "follow-up questions" in reason

    def test_complete_data_computes(self) -> None:
        mode, reason = select_mode("client", D("8"), D("400"))
        assert mode == "computed"

    def test_nobody_workflow_cannot_be_computed_even_with_data(self) -> None:
        with pytest.raises(ValueError, match="qualitative only"):
            delegation_estimate(
                WorkflowInput("nobody", D("8"), D("400")),
                Band(D("75"), D("90"), D("100")), D("120"),
            )


# --- revenue lever (quarantined) -------------------------------------------------------


class TestRevenueGain:
    def test_reported_per_scenario(self) -> None:
        gain = revenue_gain(D("50"), D("500"), Band(D("10"), D("15"), D("20")))
        assert gain == {
            "conservative": D("2500.00"), "expected": D("3750.00"), "optimistic": D("5000.00"),
        }

    def test_never_reaches_automation_net(self) -> None:
        inp = WorkflowInput("client", hours_per_week=D("12") / D("4.33"), hourly_cost=D("300"))
        est = automation_estimate(inp, band_point(D("75")))
        assert all(line.net == line.value for line in est.lines.values())  # labor only

    def test_negative_lead_inputs_rejected(self) -> None:
        with pytest.raises(ValueError, match="lead inputs"):
            revenue_gain(D("-1"), D("500"), Band(D("10"), D("15"), D("20")))


# --- rollup ----------------------------------------------------------------------------


class TestRollup:
    def test_multi_workflow_sum_per_scenario(self) -> None:
        automation = automation_estimate(
            WorkflowInput("client", hours_per_week=D("12") / D("4.33"), hourly_cost=D("300")),
            band_point(D("75")),
        )
        delegation = delegation_estimate(
            _lf_input(), Band(D("75"), D("90"), D("100")), D("120")
        )
        totals = rollup([automation, delegation])
        expected_net = D("2700.00") + D("7280.00")
        assert totals["conservative"] == expected_net
        assert set(totals) == {"conservative", "expected", "optimistic"}

    def test_empty_rollup_is_zero(self) -> None:
        assert all(v == D("0.00") for v in rollup([]).values())


# --- config wiring ---------------------------------------------------------------------


class TestConfigWiring:
    def test_settings_expose_version_and_bands(self) -> None:
        from django.conf import settings

        assert settings.ROI_BENCHMARKS_VERSION == "2026.10"
        for key in (
            "task_time_reduction", "handoff_share", "scenario_spread",
            "speed_to_lead_uplift", "missed_lead_recovery", "dso_days",
        ):
            assert key in settings.ROI_BENCHMARK_BANDS

    def test_engine_consumes_settings_bands(self) -> None:
        from django.conf import settings

        band = band_from(settings.ROI_BENCHMARK_BANDS["handoff_share"])
        est = delegation_estimate(_lf_input(), band, D("120"))
        assert est.lines["optimistic"].net == D("9688.00")

    @override_settings(ROI_BENCHMARKS_VERSION="2099.01")
    def test_version_is_overrideable(self) -> None:
        from django.conf import settings

        assert settings.ROI_BENCHMARKS_VERSION == "2099.01"

    def test_band_shapes_are_monotonic(self) -> None:
        from django.conf import settings

        for key, cfg in settings.ROI_BENCHMARK_BANDS.items():
            low, mid, high = (Decimal(str(cfg[k])) for k in ("low", "mid", "high"))
            assert low <= mid <= high, key
