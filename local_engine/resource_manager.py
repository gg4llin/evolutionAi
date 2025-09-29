"""Resource pool management for AdaptiveAgent jobs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ResourceChunk:
    compute_units: int
    memory_mb: int
    bandwidth_mbps: int
    threads: int


class InsufficientResourcesError(RuntimeError):
    """Raised when the pool cannot satisfy the requested resources."""


class ResourcePool:
    def __init__(
        self,
        *,
        compute_units_total: int,
        memory_mb_total: int,
        bandwidth_mbps_total: int,
        max_threads: int,
        min_chunk: Dict[str, int],
    ) -> None:
        self._totals = ResourceChunk(
            compute_units=compute_units_total,
            memory_mb=memory_mb_total,
            bandwidth_mbps=bandwidth_mbps_total,
            threads=max_threads,
        )
        self._available = ResourceChunk(
            compute_units=compute_units_total,
            memory_mb=memory_mb_total,
            bandwidth_mbps=bandwidth_mbps_total,
            threads=max_threads,
        )
        self._min_chunk = min_chunk

    def allocate(self, request: Dict[str, int]) -> ResourceChunk:
        """Allocate a chunk of resources if available, otherwise raise."""
        compute_units = max(request.get("compute_units", 0), self._min_chunk.get("compute_units", 0))
        memory_mb = max(request.get("memory_mb", 0), self._min_chunk.get("memory_mb", 0))
        bandwidth_mbps = max(request.get("bandwidth_mbps", 0), self._min_chunk.get("bandwidth_mbps", 0))
        threads_requested = request.get("threads", compute_units // max(self._min_chunk.get("compute_units", 1), 1))
        threads = min(threads_requested, self._available.threads)

        if not self._has_capacity(compute_units, memory_mb, bandwidth_mbps, threads):
            raise InsufficientResourcesError("Resource pool cannot satisfy the requested allocation.")

        self._available.compute_units -= compute_units
        self._available.memory_mb -= memory_mb
        self._available.bandwidth_mbps -= bandwidth_mbps
        self._available.threads -= threads

        return ResourceChunk(
            compute_units=compute_units,
            memory_mb=memory_mb,
            bandwidth_mbps=bandwidth_mbps,
            threads=threads,
        )

    def release(self, chunk: ResourceChunk) -> None:
        self._available.compute_units += chunk.compute_units
        self._available.memory_mb += chunk.memory_mb
        self._available.bandwidth_mbps += chunk.bandwidth_mbps
        self._available.threads += chunk.threads
        self._clamp_available()

    def utilisation(self) -> Dict[str, float]:
        return {
            "compute_units": self._ratio(self._available.compute_units, self._totals.compute_units),
            "memory_mb": self._ratio(self._available.memory_mb, self._totals.memory_mb),
            "bandwidth_mbps": self._ratio(self._available.bandwidth_mbps, self._totals.bandwidth_mbps),
            "threads": self._ratio(self._available.threads, self._totals.threads),
        }

    def capacity(self) -> Dict[str, int]:
        return {
            "compute_units_total": self._totals.compute_units,
            "memory_mb_total": self._totals.memory_mb,
            "bandwidth_mbps_total": self._totals.bandwidth_mbps,
            "threads_total": self._totals.threads,
        }

    def remaining(self) -> Dict[str, int]:
        return {
            "compute_units": self._available.compute_units,
            "memory_mb": self._available.memory_mb,
            "bandwidth_mbps": self._available.bandwidth_mbps,
            "threads": self._available.threads,
        }

    def _has_capacity(
        self,
        compute_units: int,
        memory_mb: int,
        bandwidth_mbps: int,
        threads: int,
    ) -> bool:
        return (
            compute_units <= self._available.compute_units
            and memory_mb <= self._available.memory_mb
            and bandwidth_mbps <= self._available.bandwidth_mbps
            and threads <= self._available.threads
        )

    def _clamp_available(self) -> None:
        self._available.compute_units = min(self._available.compute_units, self._totals.compute_units)
        self._available.memory_mb = min(self._available.memory_mb, self._totals.memory_mb)
        self._available.bandwidth_mbps = min(self._available.bandwidth_mbps, self._totals.bandwidth_mbps)
        self._available.threads = min(self._available.threads, self._totals.threads)

    @staticmethod
    def _ratio(available: int, total: int) -> float:
        if total == 0:
            return 0.0
        return round(1 - (available / total), 4)
