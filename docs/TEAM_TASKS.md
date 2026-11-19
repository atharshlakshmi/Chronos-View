# Four-person task board (Nov 18–24)

## Shared rules
- Keep the experiment ID `berkeley_site01_trial01` unless the team explicitly changes it.
- Compare identical input `data/crops/<image_id>/view_000.png` at 512 x 512.
- Record provenance, permission, model ID, seed, resolution, steps/strength, prompt, and any manual selection.
- Do not commit restricted original or modified imagery to GitHub.
- When changing input crops, notify the group immediately; downstream results become noncomparable.

## Member 1 — Data + panorama
- [ ] Confirm right to reuse selected 360 image and its date, license and attribution.
- [ ] Save permitted copy as `data/raw/<image_id>.png`.
- [ ] Add metadata row to `data/source_manifest.csv`.
- [ ] Run `python src/crop_panorama.py --input ... --outdir data/crops/<image_id>`.
- [ ] Visually inspect `view_000.png` through `view_300.png`; check wrap and overlap.
- [ ] Share the permitted `view_000.png` with M2, M3 and M4.
- [ ] Open PR `feat/data-crops` with the script, instructions, and nonrestricted visual evidence.

## Member 2 — Depth + ControlNet
- [ ] Read `notebooks/README.md`; run `src/depth.py` on the shared crop.
- [ ] Save the depth visualization with exact same size and record the model/checkpoint.
- [ ] Run depth-conditioned img2img with SD 1.5 compatible base + depth ControlNet checkpoint.
- [ ] Test low denoising strengths (starting suggestions: 0.2, 0.3, 0.4).
- [ ] Record prompt, seed, conditioning scale, strength, and qualitative structure changes.
- [ ] Share chosen result + notable failure and open PR `feat/depth-controlnet`.

## Member 3 — IC-Light
- [ ] Read official IC-Light README and run its demo on the same crop.
- [ ] Capture at least one relit output and an unsuccessful case if available.
- [ ] Record settings, version and failures (especially content hallucinations).
- [ ] If IC-Light cannot accommodate a full street scene, explain clearly; do not substitute results from a different input.
- [ ] Open PR `feat/ic-light` with reproducible notebook or commands.

## Member 4 — Baseline + comparison
- [ ] Run `src/color_grade.py` on shared view_000.
- [ ] Generate a side-by-side panel with `src/contact_sheet.py` once other results are available.
- [ ] Run `src/evaluate.py` for original/baseline and all output images.
- [ ] Visually document object shape changes, edge failures, and lighting differences.
- [ ] Pilot an overlapping-view blending test; do not label a six-view horizon ring a full 360 output.
- [ ] Update `docs/checkin1_template.md` and open PR `feat/baseline-eval`.

## Team checkpoints
- Nov 18: assign ownership; make GitHub and shared input channel; resolve image licensing.
- Nov 19: M1 supplies one crop; M2/M3 can start with a permitted temporary sample in parallel.
- Nov 20: M2 supplies depth; M4 supplies baseline.
- Nov 22: model outputs due, including logged failures.
- Nov 23: compare, make a method decision, update 1-page narrative + 2 pages figures.
- Nov 24: 5–10 minute GSI check-in; at least two group members attend.

## After Check-in 1
- Nov 25–29: expand to location/year pairs, refine 360 projection and seam handling.
- Nov 30–Dec 4: Check-in 2 with panorama outputs and early metrics.
- Dec 5–7: simple viewer, A/B participant study, two-minute presentation rehearsal.
- Dec 8/10: presentation.
- Dec 15: final artifact and report.
