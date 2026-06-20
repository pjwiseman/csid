#!/usr/bin/env python3
"""Regenerate lists/all-foods.md from data/foods.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FOODS_YAML = ROOT / "data" / "foods.yaml"
OUTPUT = ROOT / "lists" / "all-foods.md"


def main() -> None:
    data = yaml.safe_load(FOODS_YAML.read_text())
    groups = {g["id"]: g["name"] for g in data["food_groups"]}
    foods = sorted(data["foods"], key=lambda f: f["name"].lower())

    lines = [
        "# All foods (CSID elimination baseline)",
        "",
        "Single-page reference for every food in [data/foods.yaml](../data/foods.yaml). "
        "Use **Find** (Ctrl+F / Cmd+F) to search by name, category, or status.",
        "",
        "Individual tolerance varies — see [good-foods.md](./good-foods.md) and "
        "[bad-foods.md](./bad-foods.md) for grouped lists and context.",
        "",
        "Source: [Ideal Nutrition — CSID management guide](https://www.idealnutrition.com.au/csid-how-to-manage-sucrase-isomaltase-deficiency/)",
        "",
        "| Food | Status | Category | Concerns | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]

    for food in foods:
        name = food["name"].replace("|", "\\|")
        status = "Good" if food["status"] == "good" else "Bad"
        category = groups.get(food.get("group", ""), food.get("group", ""))
        concerns = ", ".join(food.get("concerns", [])) or "—"
        notes = (food.get("notes") or "—").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {name} | {status} | {category} | {concerns} | {notes} |")

    good = sum(1 for food in foods if food["status"] == "good")
    bad = len(foods) - good
    lines.extend(["", f"**Total:** {len(foods)} foods ({good} good, {bad} bad)", ""])

    OUTPUT.write_text("\n".join(lines))
    print(f"Wrote {OUTPUT} ({len(foods)} foods)")


if __name__ == "__main__":
    main()
