"""Repository and analytics for tadpole metadata."""
from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from typing import Dict, List

from .rubric_profile import RubricProfile


@dataclass
class MetadataRecord:
    worker_id: str
    specialization: str
    metrics: Dict[str, float]
    timestamp: float


class MetadataRepository:
    """Captures worker metadata and provides aggregate insights."""

    def __init__(self, rubric: RubricProfile) -> None:
        self._rubric = rubric
        self._records: List[MetadataRecord] = []

    def ingest(self, worker_id: str, specialization: str, metrics: Dict[str, float]) -> None:
        if not metrics:
            return
        now = time.time()
        self._records.append(MetadataRecord(worker_id, specialization, metrics, now))
        if len(self._records) > 1000:
            self._records = self._records[-1000:]

    def metrics_mean(self) -> Dict[str, float]:
        if not self._records:
            return {}
        aggregated: Dict[str, List[float]] = {}
        for record in self._records:
            for key, value in record.metrics.items():
                if isinstance(value, (int, float)):
                    aggregated.setdefault(key, []).append(float(value))
        return {key: statistics.fmean(values) for key, values in aggregated.items() if values}

    def principle_averages(self) -> Dict[str, float]:
        if not self._records:
            return {}
        aggregated: Dict[str, List[float]] = {}
        for record in self._records:
            numeric_metrics = {k: v for k, v in record.metrics.items() if isinstance(v, (int, float))}
            breakdown = self._rubric.principle_breakdown(numeric_metrics)
            for principle, score in breakdown.items():
                aggregated.setdefault(principle, []).append(score)
        return {key: statistics.fmean(values) for key, values in aggregated.items() if values}

    def specialization_summary(self) -> Dict[str, Dict[str, float]]:
        summary: Dict[str, Dict[str, List[float]]] = {}
        for record in self._records:
            breakdown = self._rubric.principle_breakdown(record.metrics)
            bucket = summary.setdefault(record.specialization, {})
            for principle, score in breakdown.items():
                bucket.setdefault(principle, []).append(score)
        return {
            specialization: {p: statistics.fmean(scores) for p, scores in values.items() if scores}
            for specialization, values in summary.items()
        }

    def records(self) -> List[MetadataRecord]:
        return list(self._records)
