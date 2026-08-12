"""Public package interface for Fairshift Lab."""

from fairshift_lab.calibration import apply_temperature, calibration_summary, fit_temperature
from fairshift_lab.config import ExperimentConfig, ShiftConfig, ShiftKind
from fairshift_lab.experiment import ExperimentResult, run_experiment
from fairshift_lab.external_study import ExternalStudyConfig, run_external_study
from fairshift_lab.policy_study import PolicyStudyConfig, PolicyStudyResult, run_policy_study
from fairshift_lab.sensitivity import threshold_sweep
from fairshift_lab.study import StudyConfig, StudyResult, run_study

__all__ = [
    "ExperimentConfig",
    "ExperimentResult",
    "ExternalStudyConfig",
    "PolicyStudyConfig",
    "PolicyStudyResult",
    "ShiftConfig",
    "ShiftKind",
    "StudyConfig",
    "StudyResult",
    "apply_temperature",
    "calibration_summary",
    "fit_temperature",
    "run_experiment",
    "run_external_study",
    "run_policy_study",
    "run_study",
    "threshold_sweep",
]
__version__ = "1.2.0"
