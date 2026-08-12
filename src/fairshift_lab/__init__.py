"""Public package interface for Fairshift Lab."""

from fairshift_lab.calibration import apply_temperature, calibration_summary, fit_temperature
from fairshift_lab.config import ExperimentConfig, ShiftConfig, ShiftKind
from fairshift_lab.experiment import ExperimentResult, run_experiment
from fairshift_lab.sensitivity import threshold_sweep

__all__ = [
    "ExperimentConfig",
    "ExperimentResult",
    "ShiftConfig",
    "ShiftKind",
    "apply_temperature",
    "calibration_summary",
    "fit_temperature",
    "run_experiment",
    "threshold_sweep",
]
__version__ = "0.3.1"
