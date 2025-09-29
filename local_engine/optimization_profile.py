"""Optimization cycle profile extracted from recursive_optimization_engine.txt."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Cycle:
    name: str
    duration: int
    focus: str
    scope: str
    targets: List[str]
    success_criteria: Dict[str, float | bool]


CYCLES: Dict[str, Cycle] = {
    "micro_cycle": Cycle(
        name="micro_cycle",
        duration=5,
        focus="tactical_parameter_adjustment",
        scope="individual_agent_fine_tuning",
        targets=[
            "hyperparameter_adjustment",
            "resource_allocation_rebalancing",
            "communication_protocol_tuning",
            "task_scheduling_optimization",
        ],
        success_criteria={
            "performance_improvement_threshold": 0.02,
            "stability_maintenance": True,
            "resource_efficiency_gain": 0.05,
        },
    ),
    "macro_cycle": Cycle(
        name="macro_cycle",
        duration=25,
        focus="strategic_architecture_rebalancing",
        scope="system_wide_coordination",
        targets=[
            "mesh_topology_reconfiguration",
            "specialization_track_rebalancing",
            "communication_pattern_optimization",
            "resource_distribution_strategy",
        ],
        success_criteria={
            "collective_performance_improvement": 0.1,
            "emergence_facilitation": True,
            "system_resilience_enhancement": 0.08,
        },
    ),
    "meta_cycle": Cycle(
        name="meta_cycle",
        duration=100,
        focus="fundamental_architecture_evolution",
        scope="system_paradigm_transformation",
        targets=[
            "rubric_principle_evolution",
            "spawning_strategy_metamorphosis",
            "optimization_algorithm_selection",
            "system_architecture_redesign",
        ],
        success_criteria={
            "paradigm_shift_detection": True,
            "emergent_capability_development": 0.2,
            "long_term_trajectory_improvement": 0.15,
        },
    ),
}
