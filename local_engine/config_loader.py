"""Helpers for loading connectivity and orchestration configuration."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

CONNECTIVITY_PATH = (
    Path(__file__).resolve().parent.parent / "custom_gpt" / "connectivity_config.yaml"
)


def _load_yaml(path: Path) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - import guard
        raise ModuleNotFoundError(
            "PyYAML is required to read connectivity_config.yaml. Install with 'pip install pyyaml'."
        ) from exc

    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_connectivity_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the connectivity configuration with a minimal sanity check."""
    target = path or CONNECTIVITY_PATH
    data = _load_yaml(target)
    if not isinstance(data, dict) or "connectivity" not in data:
        raise ValueError(f"Unexpected connectivity schema in {target}")
    return data["connectivity"]


def dump_example_config() -> str:
    """Return a JSON string of the connectivity block for quick diagnostics."""
    config = load_connectivity_config()
    return json.dumps(config, indent=2)
