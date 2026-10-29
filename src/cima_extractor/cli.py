from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import build_project


def main() -> None:
    parser = argparse.ArgumentParser(description="Construye un knowledge pack de fichas técnicas CIMA")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_project(args.root, args.config), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

