#!/usr/bin/env python3
"""Build static site in docs/ from data/foods.yaml."""

from __future__ import annotations

import html
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csid_foods import ROOT, load_foods, load_phase1, phase1_status

SITE_SRC = ROOT / "site"
DOCS = ROOT / "docs"

ENGLISH_URL = (
    "https://www.drcarolynenglish.com/post/what-can-i-eat-with-sucrase-isomaltase-deficiency-in-australia"
)
SOURCE_URL = (
    "https://www.idealnutrition.com.au/csid-how-to-manage-sucrase-isomaltase-deficiency/"
)
CSID_CARES_URL = "https://www.csidcares.org/treatment/diet/"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def badge(status: str | None) -> str:
    if status == "good":
        return '<span class="badge good">Good</span>'
    if status == "bad":
        return '<span class="badge bad">Bad</span>'
    return "—"


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
        <a href="changes.html"{'' if nav != 'changes' else ' aria-current="page"'}>Phase changes</a>
      </nav>
    </div>
  </header>
  <main>
{body}
  </main>
  <footer>
    <p>Australia (Phase 2): <a href="{ENGLISH_URL}">English — SID in Australia (AUSNUT 2023)</a>.
    Step 1 baseline: <a href="{SOURCE_URL}">Ideal Nutrition — CSID management guide</a>.
    Tiered US lists: <a href="{CSID_CARES_URL}">CSID Cares — Choosing Your Foods</a>.</p>
    <p>Individual tolerance varies. Test portions; cultivar and country of composition matter.</p>
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


def build_index(
    good_count: int, bad_count: int, total: int, changed: int, added: int
) -> str:
    body = f"""    <h2>CSID Phase 2 (Australia)</h2>
    <p class="intro">
      Reference lists for sucrase-isomaltase deficiency using
      <strong>Australian composition</strong> (English / AUSNUT 2023; sucrose from AFCD).
      Foods with ≤1&nbsp;g sucrose <em>and</em> ≤1&nbsp;g starch per 100&nbsp;g are treated as allow.
      Higher-sucrose foods stay on the avoid list unless you are testing a defined portion.
      Passionfruit is allow at English <em>moderate</em> (1.4&nbsp;g sucrose / 100&nbsp;g).
    </p>
    <div class="cards">
      <a class="card good" href="good.html">
        <h2>Good foods</h2>
        <p>{good_count} foods in the Australian low sucrose/starch band</p>
      </a>
      <a class="card bad" href="bad.html">
        <h2>Bad foods</h2>
        <p>{bad_count} foods above the low band (portion-test if noted)</p>
      </a>
      <a class="card all" href="all-foods.html">
        <h2>All foods</h2>
        <p>Searchable table of all {total} foods</p>
      </a>
      <a class="card all" href="changes.html">
        <h2>Phase 1 → 2</h2>
        <p>{changed} reclassified, {added} added since elimination</p>
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


def build_all_foods(
    foods: list[dict], groups: dict[str, str], phase1: dict
) -> str:
    rows: list[str] = []
    for food in sorted(foods, key=lambda f: f["name"].lower()):
        p2 = food["status"]
        p1 = phase1_status(food, phase1)
        category = groups.get(food.get("group", ""), food.get("group", ""))
        concerns = ", ".join(food.get("concerns", [])) or "—"
        notes = food.get("notes") or "—"
        change = ""
        if p1 is None:
            change = "added"
        elif p1 != p2:
            change = "changed"
        rows.append(
            f'        <tr data-status="{p2}" data-phase1="{p1 or "none"}" data-change="{change}">\n'
            f"          <td>{esc(food['name'])}</td>\n"
            f'          <td class="col-status">{badge(p2)}</td>\n'
            f'          <td class="phase-col">{badge(p1)}</td>\n'
            f'          <td class="phase-col">{badge(p2)}</td>\n'
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
      Phase 1 (elimination) vs Phase 2 (Australia) columns stay hidden unless you turn them on.
    </p>
    <div class="search-bar">
      <label for="food-search">Search</label>
      <input type="search" id="food-search" placeholder="e.g. zucchini, starch, dairy…" autocomplete="off">
      <p class="toggle-row">
        <label>
          <input type="checkbox" id="show-phases">
          Show Phase 1 vs Phase 2
        </label>
      </p>
      <p class="search-meta" id="search-count">{len(foods)} foods</p>
    </div>
    <div class="table-wrap">
      <table id="foods-table">
        <thead>
          <tr>
            <th>Food</th>
            <th class="col-status">Status</th>
            <th class="phase-col">Phase 1</th>
            <th class="phase-col">Phase 2</th>
            <th>Category</th>
            <th>Concerns</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
{"".join(rows)}        </tbody>
      </table>
    </div>
    <p class="intro"><strong>Total:</strong> {len(foods)} foods ({good} good, {bad} bad).
    <a href="changes.html">Foods that changed from Phase 1 to Phase 2</a>.</p>
"""
    html_doc = page("All foods", "all", body)
    return html_doc.replace("</body>", '  <script src="search.js"></script>\n</body>')


def build_changes(
    foods: list[dict], groups: dict[str, str], phase1: dict
) -> str:
    changed: list[tuple[dict, str]] = []
    added: list[dict] = []
    for food in foods:
        p1 = phase1_status(food, phase1)
        if p1 is None:
            added.append(food)
        elif p1 != food["status"]:
            changed.append((food, p1))
    changed.sort(key=lambda item: item[0]["name"].lower())
    added.sort(key=lambda f: f["name"].lower())

    def rows_changed() -> str:
        parts: list[str] = []
        for food, p1 in changed:
            cat = groups.get(food.get("group", ""), food.get("group", ""))
            notes = food.get("notes") or "—"
            parts.append(
                "        <tr>\n"
                f"          <td>{esc(food['name'])}</td>\n"
                f"          <td>{badge(p1)}</td>\n"
                f"          <td>{badge(food['status'])}</td>\n"
                f"          <td>{esc(cat)}</td>\n"
                f'          <td class="notes">{esc(notes)}</td>\n'
                "        </tr>\n"
            )
        return "".join(parts)

    def rows_added() -> str:
        parts: list[str] = []
        for food in added:
            cat = groups.get(food.get("group", ""), food.get("group", ""))
            parts.append(
                "        <tr>\n"
                f"          <td>{esc(food['name'])}</td>\n"
                f"          <td>{badge(food['status'])}</td>\n"
                f"          <td>{esc(cat)}</td>\n"
                "        </tr>\n"
            )
        return "".join(parts)

    body = f"""    <h2>Phase 1 → Phase 2</h2>
    <p class="intro">
      <strong>Phase 1</strong> is the Ideal Nutrition elimination list.
      <strong>Phase 2</strong> is the current Australian SSRD list.
      Passionfruit stayed allow; it is English <em>moderate</em> (1.4&nbsp;g sucrose / 100&nbsp;g), not a category change.
    </p>

    <h3>Reclassified ({len(changed)})</h3>
    <p class="intro">Listed in Phase 1, different good/bad status now.</p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Food</th>
            <th>Phase 1</th>
            <th>Phase 2</th>
            <th>Category</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
{rows_changed()}        </tbody>
      </table>
    </div>

    <h3>Added in Phase 2 ({len(added)})</h3>
    <p class="intro">Not on the Phase 1 list under this name (new foods or cultivar splits).</p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Food</th>
            <th>Phase 2</th>
            <th>Category</th>
          </tr>
        </thead>
        <tbody>
{rows_added()}        </tbody>
      </table>
    </div>
"""
    return page("Phase changes", "changes", body)


def main() -> None:
    _data, foods, groups = load_foods()
    phase1 = load_phase1()

    good_foods = [f for f in foods if f["status"] == "good"]
    bad_foods = [f for f in foods if f["status"] != "good"]
    changed = 0
    added = 0
    for food in foods:
        p1 = phase1_status(food, phase1)
        if p1 is None:
            added += 1
        elif p1 != food["status"]:
            changed += 1

    DOCS.mkdir(exist_ok=True)
    shutil.copy2(SITE_SRC / "style.css", DOCS / "style.css")
    shutil.copy2(SITE_SRC / "search.js", DOCS / "search.js")

    (DOCS / "index.html").write_text(
        build_index(len(good_foods), len(bad_foods), len(foods), changed, added)
    )
    (DOCS / "good.html").write_text(
        build_status_page(
            "good",
            "Good foods",
            "Foods that meet the Australian low sucrose and starch band (≤1 g of each per 100 g), "
            "plus fibre foods that fit that load per typical serve, and passionfruit "
            "(moderate, 1.4 g sucrose / 100 g). Test your own tolerance.",
            good_foods,
            groups,
        )
    )
    (DOCS / "bad.html").write_text(
        build_status_page(
            "bad",
            "Bad foods",
            "Foods above the Australian ≤1 g/100 g low band for sucrose and/or starch. "
            "Some have a calculated ~1 g sucrose portion for Phase 2 testing — see notes.",
            bad_foods,
            groups,
        )
    )
    (DOCS / "all-foods.html").write_text(build_all_foods(foods, groups, phase1))
    (DOCS / "changes.html").write_text(build_changes(foods, groups, phase1))
    (DOCS / ".nojekyll").touch()

    print(f"Built site in {DOCS} ({len(foods)} foods)")


if __name__ == "__main__":
    main()
