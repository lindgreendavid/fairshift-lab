"""Public package interface for Fairshift Lab."""

from fairshift_lab.config import ExperimentConfig, ShiftConfig, ShiftKind
from fairshift_lab.experiment import ExperimentResult, run_experiment

__all__ = [
    "ExperimentConfig",
    "ExperimentResult",
    "ShiftConfig",
    "ShiftKind",
    "run_experiment",
]
__version__ = "0.1.0"
