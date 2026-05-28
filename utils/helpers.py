from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def resource_path(*parts: str) -> Path:
    return BASE_DIR.joinpath(*parts)


def ensure_assets() -> None:
    resource_path("assets", "icons").mkdir(parents=True, exist_ok=True)
    resource_path("assets", "images").mkdir(parents=True, exist_ok=True)
