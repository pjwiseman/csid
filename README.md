# zpwi-csid

CSID (congenital sucrase-isomaltase deficiency) food tracking: good vs bad foods for managing sucrose, maltose, and starch tolerance.

## Lists

| File | Purpose |
| --- | --- |
| [lists/all-foods.md](lists/all-foods.md) | All foods on one page — search with Ctrl+F / Cmd+F |
| [lists/phase-changes.md](lists/phase-changes.md) | Foods reclassified or added from Phase 1 to Phase 2 |
| [lists/good-foods.md](lists/good-foods.md) | Human-readable allowed foods (Phase 2) |
| [lists/good-foods.md](lists/good-foods.md) | Human-readable allowed foods (elimination baseline) |
| [lists/bad-foods.md](lists/bad-foods.md) | Human-readable foods to avoid (elimination baseline) |
| [data/foods.yaml](data/foods.yaml) | Structured food database for apps and tracking |

## Reference

Baseline lists are now **Phase 2** using Australian composition from:

https://www.drcarolynenglish.com/post/what-can-i-eat-with-sucrase-isomaltase-deficiency-in-australia

(AUSNUT 2023 framework; sucrose/maltose/starch from [FSANZ AFCD](https://www.foodstandards.gov.au/science-data/food-nutrient-databases/afcd/data-files).)

Step 1 elimination history: [Ideal Nutrition](https://www.idealnutrition.com.au/csid-how-to-manage-sucrase-isomaltase-deficiency/). Overseas tiered lists: [CSID Cares](https://www.csidcares.org/treatment/diet/).

Some entries also cite secondary CSID sources when the baseline is silent or conflicts — see `meta.research_sources` and per-food `sources` in [data/foods.yaml](data/foods.yaml). Research workflow and source list: [.cursor/rules/project-scope-and-references.mdc](.cursor/rules/project-scope-and-references.mdc).

After editing [data/foods.yaml](data/foods.yaml), regenerate outputs with:

```bash
python3 scripts/generate-all-foods.py
python3 scripts/build-site.py
```

Also update `lists/good-foods.md` and/or `lists/bad-foods.md` by hand — see [.cursor/rules/regenerate-all-foods.mdc](.cursor/rules/regenerate-all-foods.mdc). `lists/phase-changes.md` is generated.

## Cursor agent workflow

When to start a fresh chat, which mode to use, and prompt templates for common tasks: [.cursor/rules/chat-workflow.mdc](.cursor/rules/chat-workflow.mdc).

## Website

Static site source lives in [site/](site/); built HTML is written to [docs/](docs/).

**Local preview:**

```bash
python3 scripts/build-site.py
python3 -m http.server --directory docs
```

Open http://localhost:8000

**GitHub Pages:** Push to `main`. The [pages workflow](.github/workflows/pages.yml) builds and deploys automatically. In the repo on GitHub, go to **Settings → Pages → Build and deployment** and set **Source** to **GitHub Actions** (once, after the first push with the workflow).

Tolerance is individual. Use the Australian low-low band as the Phase 2 starting point, then test defined portions of higher-sucrose foods one at a time and record symptoms.
