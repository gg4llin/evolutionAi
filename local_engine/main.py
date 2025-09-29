"""Entry point for running the AdaptiveAgent local engine."""
from __future__ import annotations

import argparse
from pathlib import Path

from .api_server import serve_forever


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AdaptiveAgent local control-plane API.")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default: 8080)")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional path to an alternate connectivity_config.yaml",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    serve_forever(args.host, args.port, config_path=args.config)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
