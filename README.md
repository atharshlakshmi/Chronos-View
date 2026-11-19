# Chronos-View — CS180 Final Project

Purpose: compare historical street scenes under a consistent golden-hour look while preserving what actually changed between years.

Team process, task board, schedule and the Check-in 1 template are in [docs/TEAM.md](docs/TEAM.md).

## Directory structure
```
Chronos-View/
├── config/
│   └── experiment.json        # Shared experiment settings
├── data/                      # Inputs (raw/, crops/, depth/ are Git-ignored)
│   ├── raw/                   # Licensed source panoramas
│   ├── crops/<image_id>/      # Six horizontal views: view_000.png … view_300.png
│   ├── depth/<image_id>/      # Depth maps matching each crop
│   └── source_manifest.csv    # Provenance and license for every image
├── docs/
│   ├── TEAM.md                # Workflow, task board, schedule, check-in template
│   └── experiment_log.csv     # Generation parameters for every run
├── notebooks/                 # Model experiments (controlnet.ipynb, ic_light.ipynb)
├── outputs/                   # Results, Git-ignored (baseline/, controlnet/, ic_light/)
├── src/
│   ├── crop_panorama.py       # Panorama → six perspective crops
│   ├── depth.py               # Depth Anything V2 depth estimation
│   ├── color_grade.py         # Warm-tone color grading baseline
│   ├── contact_sheet.py       # Side-by-side comparison panel
│   └── evaluate.py            # Compare original vs. output images
├── requirements-base.txt      # Core dependencies
└── requirements-depth.txt     # Extra dependencies for depth estimation
```

## Owner assignments
- Member 1: Data provenance, panoramic image handoff and crop conversion.
- Member 2: Depth Anything V2, depth ControlNet img2img.
- Member 3: IC-Light experiment.
- Member 4: Simple warm-tone baseline, evaluations, stitching investigation and check-in integration.

## Quick start
Use Python 3.10 or 3.11 (choose one common minor version with the team).

```bash
python -m venv .venv
source .venv/bin/activate             # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements-base.txt
python src/crop_panorama.py --input data/raw/site01_YYYY.png --outdir data/crops/site01_YYYY
python src/color_grade.py --input data/crops/site01_YYYY/view_000.png --output outputs/baseline/site01_YYYY/view_000.png
python src/evaluate.py --original data/crops/site01_YYYY/view_000.png --output outputs/baseline/site01_YYYY/view_000.png
```

For optional local depth estimation:
```bash
python -m pip install -r requirements-depth.txt
python src/depth.py --input data/crops/site01_YYYY/view_000.png --output data/depth/site01_YYYY/view_000.png
```

## Data (`data/`)
- Place licensed source panoramic imagery in `data/raw/` (ignored by Git).
- Do not distribute copyrighted/terms-restricted panoramas via the repository.
- Use `data/source_manifest.csv` with one entry per image: `image_id,source_url,creator,license,attribution,capture_date,location,notes`.
- Crops: `data/crops/<image_id>/view_000.png`, `view_060.png`, ..., `view_300.png`.
- Depth: `data/depth/<image_id>/view_000.png`, etc.
- Every model compares the exact same crop at the exact same resolution.
- For legal sharing, use only images your group is permitted to copy, process and show, with attribution.

## Outputs (`outputs/`)
- `outputs/ic_light/<image_id>/view_000.png`
- `outputs/controlnet/<image_id>/view_000.png`
- `outputs/baseline/<image_id>/view_000.png`
- `outputs/comparison.png`

Outputs are Git-ignored by default. For check-in, store permitted figures in presentation materials with attribution.
Record generation parameters in your pull-request description and in `docs/experiment_log.csv`.

## Model notebooks (`notebooks/`)
- **Member 2:** create `controlnet.ipynb` for Depth Anything V2 + `StableDiffusionControlNetImg2ImgPipeline`.
  Model: https://huggingface.co/lllyasviel/sd-controlnet-depth — Docs: https://huggingface.co/docs/diffusers/api/pipelines/controlnet
- **Member 3:** create `ic_light.ipynb` or a wrapper for the original IC-Light demo (https://github.com/lllyasviel/IC-Light).
  Important: this model is trained for foreground relighting and might fail for outdoor whole-street scenes. Do not claim preservation until visually verified.

Use a Colab GPU or a suitable local GPU. Store model weights in the runtime or cache, not in this repository.
Output PNG files go into the local `outputs/` folder or an access-controlled team shared folder, provided their license allows reuse.

## Important boundaries
- The six horizontal views are NOT a complete 360-degree panorama. Additional vertical views or a different stitching strategy is necessary for the sky/ground.
- The baseline is simple warm color grading; it does not create new physical shadows.
- Use imagery only under terms that permit your planned analysis and presentations. Google Map Tiles API documentation restricts copying, bulk downloading, and independent display/reuse of imagery. Consider properly attributed Mapillary imagery, and verify whether it supports the locations and years you need.
- The model notebooks are work assignments, not finished implementations; integrate them after testing official repositories.

## Shared resources
- Cropping: https://github.com/sunset1995/py360convert
- Depth Anything V2: https://github.com/DepthAnything/Depth-Anything-V2
- IC-Light: https://github.com/lllyasviel/IC-Light
- ControlNet depth: https://huggingface.co/lllyasviel/sd-controlnet-depth
- Diffusers: https://huggingface.co/docs/diffusers/api/pipelines/controlnet
- Mapillary licensing: https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data
- Google Map Tiles API terms: https://developers.google.com/maps/documentation/tile/policies

## Check-in 1
By Nov 24: one real licensed input, six crops, depth map, IC-Light test, ControlNet test, color baseline, and documented decision. A failed method with useful analysis is still a result. See the template in [docs/TEAM.md](docs/TEAM.md#check-in-1-template).
