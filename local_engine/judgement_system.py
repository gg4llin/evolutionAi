"""Dynamic judgement and egg revision recommendations."""
from __future__ import annotations

from typing import Dict, List

from .metadata_repository import MetadataRepository


class JudgementSystem:
    """Synthesizes metadata into actionable egg revisions."""

    def __init__(self, repository: MetadataRepository) -> None:
        self._repository = repository

    def build_revision(self) -> Dict[str, List[Dict[str, str]]]:
        principle_scores = self._repository.principle_averages()
        specialization_scores = self._repository.specialization_summary()
        recommendations: List[Dict[str, str]] = []

        def add_adjustment(section: str, action: str, rationale: str) -> None:
            recommendations.append({
                "section": section,
                "action": action,
                "rationale": rationale,
            })

        def principle_below(name: str, threshold: float) -> bool:
            return principle_scores.get(name, 1.0) < threshold

        if principle_below("efficiency_optimization", 0.55):
            add_adjustment(
                "egg_template.adaptive_modules.performance_tuner.parameters.exploration_weight",
                "decrease",
                "Efficiency lag indicates over-exploration; tighten acquisition balance to stabilize tuning.",
            )
            add_adjustment(
                "egg_template.resource_allocation.cpu_quota",
                "increase",
                "Allocating more compute mitigates observed efficiency shortfall during fine-tuning.",
            )

        if principle_below("learning_velocity", 0.6):
            add_adjustment(
                "egg_template.modular_components.learning_accelerator.parameters.adaptation_steps",
                "increase",
                "Learning velocity trailing expectations; deeper MAML adaptation improves responsiveness.",
            )
            add_adjustment(
                "egg_template.initialization_parameters.specialization.adaptation_bias",
                "shift_to_adaptive",
                "Bias new tadpoles toward adaptive tracks to capture faster learning pathways.",
            )

        if principle_below("collaborative_synergy", 0.6):
            add_adjustment(
                "egg_template.adaptive_modules.collaboration_optimizer.parameters.cooperation_incentive",
                "increase",
                "Collaboration metrics lag; reinforcing cooperative incentives should raise synergy.",
            )

        if principle_below("adaptive_resilience", 0.58):
            add_adjustment(
                "egg_template.adaptive_modules.failure_analyzer.parameters.significance_level",
                "decrease",
                "Lowering significance improves anomaly sensitivity after resilience dips.",
            )
            add_adjustment(
                "modular_components.operational_modules.resource_manager.parameters.rebalancing_frequency",
                "increase",
                "Faster rebalancing mitigates resilience regressions seen in metadata logs.",
            )

        if principle_below("innovation_capacity", 0.6):
            add_adjustment(
                "specialization_tracks.explorer.specialized_modules.creative_reasoning_engine.divergent_thinking_weight",
                "increase",
                "Innovation lag warrants boosting divergent reasoning for explorer lineage.",
            )

        if not recommendations:
            add_adjustment(
                "egg_template.initialization_parameters.performance_targets.initial_performance_target",
                "increase",
                "All rubric signals healthy; lift baseline expectations before next spawn.",
            )

        return {
            "adjustments": recommendations,
            "principle_scores": principle_scores,
            "specialization_scores": specialization_scores,
        }
