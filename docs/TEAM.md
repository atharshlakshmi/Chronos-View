# Team Guide

Project overview, setup, and data/output layout are in the [README](../README.md).

## GitHub workflow
1. Clone the single shared repository. Everyone works on their own feature branch:
   `git switch -c feat/data-crops` or `feat/depth-controlnet`, `feat/ic-light`, `feat/baseline-eval`.
2. Run `git pull --ff-only origin main` while on `main` before creating a fresh branch.
3. Write code only in your owned files unless coordinated with another owner.
4. Test your work, document your experiment parameters, then:
   `git add src/...` (or your owned notebook), `git commit -m "..."`, `git push -u origin <branch>`.
5. Open a GitHub pull request into main; ask one teammate to review; merge only when tests and input/output filenames align.
6. After merge, teammates on main run `git pull origin main`.
7. Never commit Google Street View downloads, large weights, credentials or private keys.
8. Everyone reports: done, blocker, next action at daily 10-minute standups.

## Task board (Nov 18–24)

### Shared rules
- Keep the experiment ID `berkeley_site01_trial01` unless the team explicitly changes it.
- Compare identical input `data/crops/<image_id>/view_000.png` at 512 x 512.
- Record provenance, permission, model ID, seed, resolution, steps/strength, prompt, and any manual selection.
- Do not commit restricted original or modified imagery to GitHub.
- When changing input crops, notify the group immediately; downstream results become noncomparable.

### Member 1 — Data + panorama
- [ ] Confirm right to reuse selected 360 image and its date, license and attribution.
- [ ] Save permitted copy as `data/raw/<image_id>.png`.
- [ ] Add metadata row to `data/source_manifest.csv`.
- [ ] Run `python src/crop_panorama.py --input ... --outdir data/crops/<image_id>`.
- [ ] Visually inspect `view_000.png` through `view_300.png`; check wrap and overlap.
- [ ] Share the permitted `view_000.png` with M2, M3 and M4.
- [ ] Open PR `feat/data-crops` with the script, instructions, and nonrestricted visual evidence.

### Member 2 — Depth + ControlNet
- [ ] Read the "Model notebooks" section of the README; run `src/depth.py` on the shared crop.
- [ ] Save the depth visualization with exact same size and record the model/checkpoint.
- [ ] Run depth-conditioned img2img with SD 1.5 compatible base + depth ControlNet checkpoint.
- [ ] Test low denoising strengths (starting suggestions: 0.2, 0.3, 0.4).
- [ ] Record prompt, seed, conditioning scale, strength, and qualitative structure changes.
- [ ] Share chosen result + notable failure and open PR `feat/depth-controlnet`.

### Member 3 — IC-Light
- [ ] Read official IC-Light README and run its demo on the same crop.
- [ ] Capture at least one relit output and an unsuccessful case if available.
- [ ] Record settings, version and failures (especially content hallucinations).
- [ ] If IC-Light cannot accommodate a full street scene, explain clearly; do not substitute results from a different input.
- [ ] Open PR `feat/ic-light` with reproducible notebook or commands.

### Member 4 — Baseline + comparison
- [x] Run `src/color_grade.py` on shared view_000.
- [ ] Generate a side-by-side panel with `src/contact_sheet.py` once other results are available.
- [ ] Run `src/evaluate.py` for original/baseline and all output images.
- [ ] Visually document object shape changes, edge failures, and lighting differences.
- [ ] Pilot an overlapping-view blending test; do not label a six-view horizon ring a full 360 output.
- [ ] Fill in the Check-in 1 template below and open PR `feat/baseline-eval`.

## Schedule

### Before Check-in 1
- Nov 18: assign ownership; make GitHub and shared input channel; resolve image licensing.
- Nov 19: M1 supplies one crop; M2/M3 can start with a permitted temporary sample in parallel.
- Nov 20: M2 supplies depth; M4 supplies baseline.
- Nov 22: model outputs due, including logged failures.
- Nov 23: compare, make a method decision, update 1-page narrative + 2 pages figures.
- Nov 24: 5–10 minute GSI check-in; at least two group members attend.

### After Check-in 1
- Nov 25–29: expand to location/year pairs, refine 360 projection and seam handling.
- Nov 30–Dec 4: Check-in 2 with panorama outputs and early metrics.
- Dec 5–7: simple viewer, A/B participant study, two-minute presentation rehearsal.
- Dec 8/10: presentation.
- Dec 15: final artifact and report.

## Check-in 1 template
Due November 24. Negative results are acceptable if accurately described. The GSI check-in lasts 5–10 minutes; at least two members attend. The updated proposal is about 1 page of narrative plus ~2 pages of figures.

### Objective (plain English)
Make photos of the same street across different years look like they were taken at the same time of day, without changing historical objects.

### Data
- Where image came from and applicable permission/license:
- Location and capture date:
- Image dimensions, coverage, known defects:

### Completed experiments
- Panorama crop: show original + six crops (or explain why unavailable)
- Depth Anything V2: show depth map
- A. IC-Light: show real output and generation settings
- B. Depth ControlNet img2img: show real output and generation settings
- C. Warm color grade baseline: show real output
- Seam blending: show test or explain blockers

### Comparison and findings
- Lighting consistency:
- Structures unchanged / hallucinations (document examples):
- Crop seams:
- Which method wins and why?

### Next experiment after feedback
- Single most important assumption to test:
- One feasible next step:
