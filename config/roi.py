"""ROI benchmark configuration — platform-level settings, versioned in git.

This is SETTINGS, not per-user data: one global set of bands, edited only by
the superuser through the repo (git is the access control). Providers never
see or edit it; the engine reads it at compute time; every Estimate snapshots
the version + values it used, so config changes never shift a stored proposal.

Research & rationale: docs/design/pricing-benefit-research.md (§B benchmark
levers). Change values => bump ROI_BENCHMARKS_VERSION.
"""

ROI_BENCHMARKS_VERSION = "2026.10"

ROI_BENCHMARK_BANDS = {
    # Automation lever — % of a workflow's task time removed by a rule-based flow.
    "task_time_reduction": {
        "low": 40, "mid": 60, "high": 80, "unit": "%",
        "source": "rule-based flows; draft rows 40–70 (support triage, data entry), "
                  "60–75 (content/calendar)",
    },
    # Delegation scenarios — share of the workflow handed to the VA
    # (LF case: 8 hrs/wk × 4.33 × 75/90/100% → 26.0 / 31.2 / 34.6 hrs/mo).
    "handoff_share": {
        "low": 75, "mid": 90, "high": 100, "unit": "%",
        "source": "conservative-to-full handoff; provider-editable per estimate",
    },
    # Generic fallback spread when a lever has no band (× base hours/value).
    "scenario_spread": {
        "low": 1.0, "mid": 1.2, "high": 1.33, "unit": "×",
        "source": "LF case anchors: 26 / 31.2 / 34.6 hrs",
    },
    # Revenue levers — computed only when the session captured lead data (Cards 6+);
    # reported separately, never folded into labor payback.
    "speed_to_lead_uplift": {
        "low": 10, "mid": 15, "high": 20, "unit": "%",
        "source": "draft band kept conservative vs 21×/5-min industry hype",
    },
    "missed_lead_recovery": {
        "low": 10, "mid": 20, "high": 30, "unit": "%",
        "source": "draft hypothesis + CRM-cleanup lore; verify per pilot",
    },
    "dso_days": {
        "low": 5, "mid": 10, "high": 15, "unit": "days",
        "source": "AR-automation vendor case studies; self-interested source, band kept wide",
    },
}
