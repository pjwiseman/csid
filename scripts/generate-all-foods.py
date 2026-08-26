#!/usr/bin/env python3
"""Regenerate lists/all-foods.md and lists/phase-changes.md from data/foods.yaml."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csid_foods import ROOT, label, load_foods, load_phase1, phase1_status

OUTPUT = ROOT / "lists" / "all-foods.md"
CHANGES = ROOT / "lists" / "phase-changes.md"


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def write_all_foods(foods: list[dict], groups: dict[str, str]) -> None:
    lines = [
        "# All foods (CSID Phase 2 — Australian SSRD)",
        "",
        "Single-page reference for every food in [data/foods.yaml](../data/foods.yaml). "
        "Use **Find** (Ctrl+F / Cmd+F) to search by name, category, or status.",
        "",
        "Individual tolerance varies — see [good-foods.md](./good-foods.md) and "
        "[bad-foods.md](./bad-foods.md) for grouped lists. "
        "Phase 1 → Phase 2 category changes: [phase-changes.md](./phase-changes.md). "
        "On the website, Phase 1/Phase 2 columns on [all foods](../docs/all-foods.html) "
        "are hidden until you tick **Show Phase 1 vs Phase 2**.",
        "",
        "Source: [English — SID in Australia](https://www.drcarolynenglish.com/post/what-can-i-eat-with-sucrase-isomaltase-deficiency-in-australia) "
        "(AUSNUT 2023 / AFCD). Step 1 baseline: "
        "[Ideal Nutrition — CSID management guide](https://www.idealnutrition.com.au/csid-how-to-manage-sucrase-isomaltase-deficiency/)",
        "",
        "| Food | Status (Phase 2) | Category | Concerns | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]

    for food in foods:
        name = md_escape(food["name"])
        status = label(food["status"])
        category = groups.get(food.get("group", ""), food.get("group", ""))
        concerns = ", ".join(food.get("concerns", [])) or "—"
        notes = md_escape(food.get("notes") or "—")
        lines.append(f"| {name} | {status} | {category} | {concerns} | {notes} |")

    good = sum(1 for food in foods if food["status"] == "good")
    bad = len(foods) - good
    lines.extend(["", f"**Total:** {len(foods)} foods ({good} good, {bad} bad)", ""])
    OUTPUT.write_text("\n".join(lines))
    print(f"Wrote {OUTPUT} ({len(foods)} foods)")


def write_phase_changes(
    foods: list[dict], groups: dict[str, str], phase1: dict
) -> None:
    changed: list[dict] = []
    added: list[dict] = []
    for food in foods:
        p1 = phase1_status(food, phase1)
        p2 = food["status"]
        if p1 is None:
            added.append(food)
        elif p1 != p2:
            changed.append({**food, "phase1_status": p1})

    changed.sort(key=lambda f: f["name"].lower())
    added.sort(key=lambda f: f["name"].lower())

    lines = [
        "# Phase 1 → Phase 2 category changes",
        "",
        "**Phase 1** is the Ideal Nutrition disaccharide-free elimination list "
        "(including foods added before the Australian reassess). "
        "**Phase 2** is the current Australian SSRD list "
        "([English](https://www.drcarolynenglish.com/post/what-can-i-eat-with-sucrase-isomaltase-deficiency-in-australia) / AUSNUT / AFCD).",
        "",
        "Lookup table: [data/phase1.yaml](../data/phase1.yaml). "
        "Website: [changes.html](../docs/changes.html). "
        "Optional Phase 1/Phase 2 columns: [all-foods.html](../docs/all-foods.html).",
        "",
        "## Reclassified",
        "",
        "Foods that existed in Phase 1 and now have a different good/bad status.",
        "",
        "| Food | Phase 1 | Phase 2 | Category | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for food in changed:
        cat = groups.get(food.get("group", ""), food.get("group", ""))
        notes = md_escape(food.get("notes") or "—")
        lines.append(
            f"| {md_escape(food['name'])} | {label(food['phase1_status'])} | "
            f"{label(food['status'])} | {cat} | {notes} |"
        )
    if not changed:
        lines.append("| — | — | — | — | — |")

    lines.extend(
        [
            "",
            f"**{len(changed)}** reclassified.",
            "",
            "## Added in Phase 2",
            "",
            "Not on the Phase 1 list under this name (new cultivar splits, Australian "
            "Table 1–2 foods, or portion-listed nuts/seeds).",
            "",
            "| Food | Phase 2 | Category |",
            "| --- | --- | --- |",
        ]
    )
    for food in added:
        cat = groups.get(food.get("group", ""), food.get("group", ""))
        lines.append(f"| {md_escape(food['name'])} | {label(food['status'])} | {cat} |")
    lines.extend(["", f"**{len(added)}** added.", ""])

    CHANGES.write_text("\n".join(lines))
    print(f"Wrote {CHANGES} ({len(changed)} reclassified, {len(added)} added)")


def main() -> None:
    _data, foods, groups = load_foods()
    foods_sorted = sorted(foods, key=lambda f: f["name"].lower())
    phase1 = load_phase1()
    write_all_foods(foods_sorted, groups)
    write_phase_changes(foods_sorted, groups, phase1)


if __name__ == "__main__":
    main()
