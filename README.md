# Chronos-View — CS180 Final Project

Purpose: compare historical street scenes under a consistent golden-hour look while preserving what actually changed between years.

Team process, task board, schedule and the Check-in 1 template are in [docs/TEAM.md](docs/TEAM.md).

## Directory structure
```
Chronos-View/
├── config/
│   └── experiment.json        # Shared settings for downloading and cropping
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
│   ├── download_streetview.py # Street View panoramas (current + past years) → data/raw/
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

## How to run

Run every command from the project root (the `Chronos-View/` folder). The examples use the image ID
`telegraph_bancroft_2025-03`; replace it with your own image ID.

### Step 1: Set up the environment (once)
Use Python 3.10 or 3.11 (agree on one version as a team).

```bash
python -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-base.txt
```

**macOS only:** the Street View downloader needs two system libraries. Install them once with [Homebrew](https://brew.sh):
```bash
brew install inih brotli
```

Activate the environment (`source .venv/bin/activate`) every time you open a new terminal.

### Step 2: Download panoramas
Downloads the newest Street View panorama at each spot plus older captures from earlier years.
Images are saved to `data/raw/<spot>_<YYYY-MM>.jpg`, and each one gets a row in `data/source_manifest.csv`.

Settings live in the `"download"` section of [config/experiment.json](config/experiment.json). Edit it to change
the spots or how many timestamps to download:

```json
"download": {
  "max_timestamps": 3,
  "zoom": 3,
  "outdir": "data/raw",
  "manifest": "data/source_manifest.csv",
  "spots": {
    "telegraph_bancroft": [37.8688, -122.2589],
    "shattuck_downtown": [37.87, -122.2681]
  }
}
```

Then run:
```bash
# See which years are available, without downloading anything
python src/download_streetview.py --dry-run

# Download everything set in the config
python src/download_streetview.py
```

Command-line options override the config for a one-off run:

| Option | Meaning |
|---|---|
| `--max-timestamps N` | Max captures per spot, newest first, including the current one |
| `--zoom Z` | Resolution: 3 = 4096×2048, 4 = 8192×4096 |
| `--spot NAME LAT LON` | Download this spot instead of the config's spots (repeat for several) |
| `--config PATH` | Use a different config file |
| `--overwrite` | Re-download images that already exist |
| `--dry-run` | Only list captures, download nothing |

Using an image from another source (e.g. Mapillary)? Save it as `data/raw/<image_id>.jpg` and add its row to
`data/source_manifest.csv` by hand. It must be a 2:1 equirectangular panorama.

### Step 3: Crop each panorama into six views
```bash
python src/crop_panorama.py
```
Crops every image in `data/raw/` into `data/crops/<image_id>/view_000.png` … `view_300.png` (512×512, one every 60°),
where `<image_id>` is the file name without `.jpg`. These crops are the shared input for every method.

Images that already have crops are skipped, so you can re-run it after downloading more.

Crop settings (folders, size, field of view, view angles, pitch) live in the `"crop"` section of
[config/experiment.json](config/experiment.json). Command-line options override them for a one-off run:

| Option | Meaning |
|---|---|
| `--overwrite` | Re-crop images that already have crops |
| `--input PATH` | Crop only this one panorama |
| `--size N` | Crop size in pixels |

### TO DO
Steps for depth maps, relighting (baseline, ControlNet, IC-Light), evaluation and comparison images are still in progress. This section will be updated soon.

### Troubleshooting
| Error | Fix |
|---|---|
| `Library not loaded: .../libINIReader...` or `.../libbrotlidec...` | macOS: `brew install inih brotli` |
| `CERTIFICATE_VERIFY_FAILED` | Already handled inside `download_streetview.py`. For other scripts, run `pip install certifi` and prefix the command with `SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")` |
| `Expected an approximately 2:1 equirectangular image` | The input to `crop_panorama.py` isn't a full 360° panorama |


## Shared resources
- Cropping: https://github.com/sunset1995/py360convert
- Depth Anything V2: https://github.com/DepthAnything/Depth-Anything-V2
- IC-Light: https://github.com/lllyasviel/IC-Light
- ControlNet depth: https://huggingface.co/lllyasviel/sd-controlnet-depth
- Diffusers: https://huggingface.co/docs/diffusers/api/pipelines/controlnet
- Mapillary licensing: https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data
- Google Map Tiles API terms: https://developers.google.com/maps/documentation/tile/policies

