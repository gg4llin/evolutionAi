"""Rubric profile derived from dynamic_rubric_system.txt."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Principle:
    weight: float
    metrics: Dict[str, float]


class RubricProfile:
    """Static representation of rubric principles and metric weights."""

    def __init__(self) -> None:
        self._principles: Dict[str, Principle] = {
            "efficiency_optimization": Principle(
                weight=0.25,
                metrics={
                    "execution_time": 0.4,
                    "resource_utilization": 0.35,
                    "task_completion_rate": 0.25,
                },
            ),
            "learning_velocity": Principle(
                weight=0.20,
                metrics={
                    "improvement_rate_per_iteration": 0.4,
                    "knowledge_retention_score": 0.35,
                    "pattern_recognition_accuracy": 0.25,
                },
            ),
            "collaborative_synergy": Principle(
                weight=0.20,
                metrics={
                    "inter_agent_communication_efficiency": 0.4,
                    "shared_resource_optimization": 0.35,
                    "collective_problem_solving_score": 0.25,
                },
            ),
            "adaptive_resilience": Principle(
                weight=0.15,
                metrics={
                    "error_recovery_time": 0.4,
                    "failure_prediction_accuracy": 0.35,
                    "system_stability_index": 0.25,
                },
            ),
            "innovation_capacity": Principle(
                weight=0.20,
                metrics={
                    "novel_solution_generation": 0.4,
                    "breakthrough_frequency": 0.35,
                    "creative_problem_solving_score": 0.25,
                },
            ),
        }

    @property
    def principles(self) -> Dict[str, Principle]:
        return self._principles

    def composite_score(self, metrics_payload: Dict[str, float]) -> float:
        """Compute a weighted composite score using provided metric values (0-1 scale)."""
        total = 0.0
        for principle in self._principles.values():
            principle_score = 0.0
            for metric_name, metric_weight in principle.metrics.items():
                value = metrics_payload.get(metric_name, 0.0)
                principle_score += value * metric_weight
            total += principle_score * principle.weight
        return total

    def principle_breakdown(self, metrics_payload: Dict[str, float]) -> Dict[str, float]:
        """Return per-principle weighted scores for analysis."""
        breakdown: Dict[str, float] = {}
        for name, principle in self._principles.items():
            principle_score = 0.0
            for metric_name, metric_weight in principle.metrics.items():
                value = metrics_payload.get(metric_name, 0.0)
                principle_score += value * metric_weight
            breakdown[name] = principle_score
        return breakdown
