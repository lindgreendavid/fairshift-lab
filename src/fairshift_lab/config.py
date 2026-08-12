"""Validated configuration objects for reproducible experiments."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ShiftKind(str, Enum):
    """Supported mechanisms for changing the target population."""

    NONE = "none"
    COVARIATE = "covariate"
    CONCEPT = "concept"
    PREVALENCE = "prevalence"


@dataclass(frozen=True)
class ShiftConfig:
    """Describe one controlled target-domain intervention."""

    kind: ShiftKind = ShiftKind.NONE
    magnitude: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.magnitude <= 1.0:
            raise ValueError("shift magnitude must be between 0 and 1")
        if self.kind is ShiftKind.NONE and self.magnitude != 0.0:
            raise ValueError("an unshifted population must have magnitude 0")


@dataclass(frozen=True)
class ExperimentConfig:
    """Complete inputs needed to reproduce a baseline experiment."""

    samples: int = 2_000
    seed: int = 42
    decision_threshold: float = 0.5
    learning_rate: float = 0.2
    iterations: int = 800
    bootstrap_samples: int = 200
    confidence_level: float = 0.95
    target_shift: ShiftConfig = ShiftConfig()

    def __post_init__(self) -> None:
        if self.samples < 100:
            raise ValueError("samples must be at least 100")
        if not 0.0 < self.decision_threshold < 1.0:
            raise ValueError("decision threshold must be strictly between 0 and 1")
        if self.learning_rate <= 0.0:
            raise ValueError("learning rate must be positive")
        if self.iterations < 1:
            raise ValueError("iterations must be positive")
        if self.bootstrap_samples < 20:
            raise ValueError("bootstrap samples must be at least 20")
        if not 0.5 <= self.confidence_level < 1.0:
            raise ValueError("confidence level must be between 0.5 and 1")
