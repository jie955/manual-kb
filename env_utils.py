#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""加载仓库根 .env 到 os.environ（不覆盖已设置的变量）。"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or (REPO_ROOT / ".env")
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, val)
