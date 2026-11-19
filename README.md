# Chronos-View — CS180 Final Project Starter

Purpose: compare historical street scenes under a consistent golden-hour look while preserving what actually changed between years.

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
By Nov 24: one real licensed input, six crops, depth map, IC-Light test, ControlNet test, color baseline, and documented decision. A failed method with useful analysis is still a result. See `docs/checkin1_template.md`.
