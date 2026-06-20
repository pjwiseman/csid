# zpwi-csid

CSID (congenital sucrase-isomaltase deficiency) food tracking: good vs bad foods for managing sucrose, maltose, and starch tolerance.

## Lists

| File | Purpose |
| --- | --- |
| [lists/all-foods.md](lists/all-foods.md) | All foods on one page — search with Ctrl+F / Cmd+F |
| [lists/good-foods.md](lists/good-foods.md) | Human-readable allowed foods (elimination baseline) |
| [lists/bad-foods.md](lists/bad-foods.md) | Human-readable foods to avoid (elimination baseline) |
| [data/foods.yaml](data/foods.yaml) | Structured food database for apps and tracking |

## Reference

Baseline lists follow the disaccharide-free elimination phase from:

https://www.idealnutrition.com.au/csid-how-to-manage-sucrase-isomaltase-deficiency/

Tiered tolerance lists and food-composition guidance: [CSID Cares — Choosing Your Foods](https://www.csidcares.org/treatment/diet/)

Some entries also cite secondary CSID sources when the baseline is silent or conflicts — see `meta.research_sources` and per-food `sources` in [data/foods.yaml](data/foods.yaml). Research workflow and source list: [.cursor/rules/project-scope-and-references.mdc](.cursor/rules/project-scope-and-references.mdc).

After editing [data/foods.yaml](data/foods.yaml), regenerate outputs with:

```bash
python3 scripts/generate-all-foods.py
python3 scripts/build-site.py
```

## Website

Static site source lives in [site/](site/); built HTML is written to [docs/](docs/).

**Local preview:**

```bash
python3 scripts/build-site.py
python3 -m http.server --directory docs
```

Open http://localhost:8000

**GitHub Pages:** Push to `main`. The [pages workflow](.github/workflows/pages.yml) builds and deploys automatically. In the repo on GitHub, go to **Settings → Pages → Build and deployment** and set **Source** to **GitHub Actions** (once, after the first push with the workflow).

Tolerance is individual. After 2–4 weeks on the elimination diet, reintroduce foods one at a time (small → moderate → large servings) and record symptoms before personalising your diet.
