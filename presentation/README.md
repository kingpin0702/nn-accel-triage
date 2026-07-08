# NN-Accel-Triage — Presentation

Academic presentation of the NN-Accel-Triage project, delivered in two formats
with identical content and design.

## Files

| File | What it is |
|------|-----------|
| `nn_accel_triage_deck.html` | **Interactive HTML deck** — self-contained (no CDN/assets), best for the live pipeline animation. Open in any browser. |
| `nn_accel_triage.pptx` | **Editable PowerPoint** — open/edit in PowerPoint or Google Slides. The animation is an embedded GIF that auto-plays in Slide Show mode. |
| `assets/pipeline_animation.gif` | The "system in action" pipeline data-flow animation. |

## Slide outline (9 sections · 11 slides)

1. **Title**
2. **Introduction** — why triage is the bottleneck
3. **Problem Statement** — input/output + why it is hard
4. **Objectives** — the five core objectives
5. **Methodology** — seven-stage pipeline flowchart + explanation
6. **System in Action** — animated pipeline data-flow (one failing test end-to-end)
7. **Visuals** — triage dashboard (verification / explanation / packaging)
8. **Outputs** — fault-dataset table + per-label evaluation metrics table
9. **Results & Conclusion** — method comparison + conclusion
10. **References**

## Using the HTML deck

- Navigate: `→` / `Space` (next), `←` (prev), `Home` / `End`, or click the dots.
- `F` toggles fullscreen. The slide 6 animation auto-loops while that slide is shown.
- Export to PDF: open in Chrome → Print → *Save as PDF* (Landscape).

## Rebuilding

The deck is generated from the repo's real data and dashboard renders:

```bash
python presentation/build_animation_gif.py   # → assets/pipeline_animation.gif
python presentation/build_deck_html.py        # → nn_accel_triage_deck.html
python presentation/build_deck_pptx.py        # → nn_accel_triage.pptx
```

Requires `python-pptx` and `Pillow`. Source figures come from `reports/dash_*.png`.

## Data provenance

All numbers are pulled from the project itself:
`benchmark/ground_truth.json`, `reports/benchmark_20260707.json`, and the
committed `reports/dashboard.html`. The References slide lists related-work
citations compiled for context — verify/replace specifics before final submission.
