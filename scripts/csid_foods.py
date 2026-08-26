"""Shared food-list helpers for generate-all-foods.py and build-site.py."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FOODS_YAML = ROOT / "data" / "foods.yaml"
PHASE1_YAML = ROOT / "data" / "phase1.yaml"


def load_foods() -> tuple[dict, list[dict], dict[str, str]]:
    data = yaml.safe_load(FOODS_YAML.read_text())
    groups = {g["id"]: g["name"] for g in data["food_groups"]}
    return data, data["foods"], groups


def load_phase1() -> dict:
    return yaml.safe_load(PHASE1_YAML.read_text())


def phase1_status(food: dict, phase1: dict) -> str | None:
    """Return 'good' or 'bad' if the food existed in Phase 1, else None."""
    key = phase1.get("aliases", {}).get(food["name"], food["name"])
    return phase1.get("status", {}).get(key)


def label(status: str | None) -> str:
    if status == "good":
        return "Good"
    if status == "bad":
        return "Bad"
    return "—"
