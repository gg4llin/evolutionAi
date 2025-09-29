"""Specialization tracks mirrored from agentic_replication_system.txt."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class SpecializationTrack:
    name: str
    focus_metrics: List[str]
    spawn_condition: str


TRACKS: Dict[str, SpecializationTrack] = {
    "generalist": SpecializationTrack(
        name="generalist",
        focus_metrics=["efficiency_optimization", "learning_velocity"],
        spawn_condition="baseline_operation",
    ),
    "optimizer": SpecializationTrack(
        name="optimizer",
        focus_metrics=["efficiency_optimization", "adaptive_resilience"],
        spawn_condition="system_bottleneck_detected",
    ),
    "explorer": SpecializationTrack(
        name="explorer",
        focus_metrics=["innovation_capacity", "learning_velocity"],
        spawn_condition="stagnation_detected",
    ),
    "coordinator": SpecializationTrack(
        name="coordinator",
        focus_metrics=["collaborative_synergy", "adaptive_resilience"],
        spawn_condition="communication_overhead_high",
    ),
    "analyst": SpecializationTrack(
        name="analyst",
        focus_metrics=["learning_velocity", "innovation_capacity"],
        spawn_condition="pattern_complexity_increase",
    ),
}


def resolve_specialization(trigger: Optional[str], requested: Optional[str]) -> SpecializationTrack:
    """Pick a specialization based on either request or spawn trigger."""
    if requested and requested in TRACKS:
        return TRACKS[requested]
    if trigger:
        for track in TRACKS.values():
            if track.spawn_condition == trigger:
                return track
    return TRACKS["generalist"]
