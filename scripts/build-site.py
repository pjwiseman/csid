#!/usr/bin/env python3
"""Build static site in docs/ from data/foods.yaml."""

from __future__ import annotations

import html
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FOODS_YAML = ROOT / "data" / "foods.yaml"
SITE_SRC = ROOT / "site"
DOCS = ROOT / "docs"

SOURCE_URL = (
    "https://www.idealnutrition.com.au/csid-how-to-manage-sucrase-isomaltase-deficiency/"
)
CSID_CARES_URL = "https://www.csidcares.org/treatment/diet/"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def page(title: str, nav: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} — CSID Food Lists</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <div class="wrap">
      <h1><a href="index.html">CSID Food Lists</a></h1>
      <nav>
        <a href="index.html"{'' if nav != 'home' else ' aria-current="page"'}>Home</a>
        <a href="good.html"{'' if nav != 'good' else ' aria-current="page"'}>Good foods</a>
        <a href="bad.html"{'' if nav != 'bad' else ' aria-current="page"'}>Bad foods</a>
        <a href="all-foods.html"{'' if nav != 'all' else ' aria-current="page"'}>All foods</a>
      </nav>
    </div>
  </header>
  <main>
{body}
  </main>
  <footer>
    <p>Baseline: <a href="{SOURCE_URL}">Ideal Nutrition — CSID management guide</a>.
    Tiered tolerance: <a href="{CSID_CARES_URL}">CSID Cares — Choosing Your Foods</a>.</p>
    <p>Individual tolerance varies. Reintroduce foods one at a time after 2–4 weeks on elimination.</p>
  </footer>
</body>
</html>
"""


def grouped_list_html(foods: list[dict], groups: dict[str, str]) -> str:
    by_group: dict[str, list[str]] = {}
    group_order = list(groups.keys())

    for food in foods:
        gid = food.get("group", "")
        by_group.setdefault(gid, []).append(food["name"])

    parts: list[str] = []
    for gid in group_order:
        names = by_group.get(gid)
        if not names:
            continue
        parts.append(f'    <section class="group">\n      <h2>{esc(groups[gid])}</h2>\n')
        parts.append('      <ul class="foods">\n')
        for name in sorted(names, key=str.lower):
            parts.append(f"        <li>{esc(name)}</li>\n")
        parts.append("      </ul>\n    </section>\n")

    return "".join(parts)


def build_index(good_count: int, bad_count: int, total: int) -> str:
    body = f"""    <h2>CSID elimination baseline</h2>
    <p class="intro">
      Reference lists for congenital sucrase-isomaltase deficiency (CSID):
      foods allowed and avoided during a <strong>disaccharide-free elimination diet</strong> (Step 1).
      Use these during strict elimination; reintroduce and test before assuming long-term tolerance.
    </p>
    <div class="cards">
      <a class="card good" href="good.html">
        <h2>Good foods</h2>
        <p>{good_count} foods allowed during elimination</p>
      </a>
      <a class="card bad" href="bad.html">
        <h2>Bad foods</h2>
        <p>{bad_count} foods to avoid during elimination</p>
      </a>
      <a class="card all" href="all-foods.html">
        <h2>All foods</h2>
        <p>Searchable table of all {total} foods</p>
      </a>
    </div>
"""
    return page("Home", "home", body)


def build_status_page(
    nav: str,
    heading: str,
    intro: str,
    foods: list[dict],
    groups: dict[str, str],
) -> str:
    body = f"""    <h2>{esc(heading)}</h2>
    <p class="intro">{intro}</p>
{grouped_list_html(foods, groups)}
"""
    return page(heading, nav, body)


def build_all_foods(foods: list[dict], groups: dict[str, str]) -> str:
    rows: list[str] = []
    for food in sorted(foods, key=lambda f: f["name"].lower()):
        status = food["status"]
        badge = "good" if status == "good" else "bad"
        label = "Good" if status == "good" else "Bad"
        category = groups.get(food.get("group", ""), food.get("group", ""))
        concerns = ", ".join(food.get("concerns", [])) or "—"
        notes = food.get("notes") or "—"
        rows.append(
            f'        <tr data-status="{status}">\n'
            f"          <td>{esc(food['name'])}</td>\n"
            f'          <td><span class="badge {badge}">{label}</span></td>\n'
            f"          <td>{esc(category)}</td>\n"
            f"          <td>{esc(concerns)}</td>\n"
            f'          <td class="notes">{esc(notes)}</td>\n'
            f"        </tr>\n"
        )

    good = sum(1 for f in foods if f["status"] == "good")
    bad = len(foods) - good

    body = f"""    <h2>All foods</h2>
    <p class="intro">
      Single-page reference for every food. Search by name, category, status, or concern.
    </p>
    <div class="search-bar">
      <label for="food-search">Search</label>
      <input type="search" id="food-search" placeholder="e.g. zucchini, starch, dairy…" autocomplete="off">
      <p class="search-meta" id="search-count">{len(foods)} foods</p>
    </div>
    <div class="table-wrap">
      <table id="foods-table">
        <thead>
          <tr>
            <th>Food</th>
            <th>Status</th>
            <th>Category</th>
            <th>Concerns</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
{"".join(rows)}        </tbody>
      </table>
    </div>
    <p class="intro"><strong>Total:</strong> {len(foods)} foods ({good} good, {bad} bad)</p>
"""
    html_doc = page("All foods", "all", body)
    return html_doc.replace("</body>", '  <script src="search.js"></script>\n</body>')


def main() -> None:
    data = yaml.safe_load(FOODS_YAML.read_text())
    groups = {g["id"]: g["name"] for g in data["food_groups"]}
    foods = data["foods"]

    good_foods = [f for f in foods if f["status"] == "good"]
    bad_foods = [f for f in foods if f["status"] != "good"]

    DOCS.mkdir(exist_ok=True)
    shutil.copy2(SITE_SRC / "style.css", DOCS / "style.css")
    shutil.copy2(SITE_SRC / "search.js", DOCS / "search.js")

    (DOCS / "index.html").write_text(build_index(len(good_foods), len(bad_foods), len(foods)))
    (DOCS / "good.html").write_text(
        build_status_page(
            "good",
            "Good foods",
            "Foods recommended during a disaccharide-free elimination diet (Step 1). "
            "Individual tolerance varies — reintroduce and test before assuming long-term safety.",
            good_foods,
            groups,
        )
    )
    (DOCS / "bad.html").write_text(
        build_status_page(
            "bad",
            "Bad foods",
            "Foods to avoid during a disaccharide-free elimination diet (Step 1). "
            "Many adults can tolerate some of these after structured reintroduction testing.",
            bad_foods,
            groups,
        )
    )
    (DOCS / "all-foods.html").write_text(build_all_foods(foods, groups))
    (DOCS / ".nojekyll").touch()

    print(f"Built site in {DOCS} ({len(foods)} foods)")


if __name__ == "__main__":
    main()
