# Profile graphics

All graphics are plain SVGs drawn from rectangles (own 5x7 pixel font, notched cards), using the colors from the portfolio's `style.css`.

| Script | What it does | When to run |
|---|---|---|
| `build_static.py` | Header, section headings, cert badges → `assets/*.svg` | Locally, when your certs change (edit the `DATA` block at the top) |
| `update_stats.py` | Contribution heatmap + stats/languages card → `assets/generated/` | Automatically by `.github/workflows/update-stats.yml` (on first push, then daily) |

```bash
python scripts/build_static.py                       # rebuild the static graphics
python scripts/update_stats.py --out /tmp/p --demo   # preview the live graphics with fake data
```

No dependencies beyond Python 3.
