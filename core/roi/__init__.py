"""ROI engine — deterministic, pure-Python money math (Card 3).

Public surface: core.roi.engine. Settings config: config.roi (loaded into
settings as ROI_BENCHMARKS_VERSION / ROI_BENCHMARK_BANDS).
"""

from core.roi.engine import (  # noqa: F401
    Band,
    ModeEstimate,
    ScenarioLine,
    WorkflowInput,
    automation_estimate,
    band_from,
    band_point,
    delegation_estimate,
    revenue_gain,
    rollup,
    select_mode,
)
