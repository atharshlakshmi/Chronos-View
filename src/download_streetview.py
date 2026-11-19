"""Download Google Street View panoramas (current + historical) into data/raw/.

Each spot gets its newest panorama plus older captures at the same place,
up to max_timestamps in total. Every downloaded image is recorded in
data/source_manifest.csv.

Settings (spots, max_timestamps, zoom, outdir, manifest) are read from the
"download" section of config/experiment.json. Command-line options override them.

Usage:
  python src/download_streetview.py                                   # use config/experiment.json
  python src/download_streetview.py --max-timestamps 5                # override one setting
  python src/download_streetview.py --spot telegraph_bancroft 37.8688 -122.2589   # one-off spot
  python src/download_streetview.py --dry-run                         # list captures, download nothing

IMPORTANT: Google Street View imagery is restricted by Google's terms of service.
Do not commit downloaded images, and confirm with the team that your use is permitted.
"""
import argparse
import csv
import json
import os
from pathlib import Path

import certifi

# Use certifi's certificate list so HTTPS works on python.org builds of Python.
# Must be set before any network connection is made.
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

from streetlevel import streetview  # noqa: E402

# Used when a setting is missing from both the command line and the config file
FALLBACKS = {
    "max_timestamps": 3,
    "zoom": 3,
    "outdir": "data/raw",
    "manifest": "data/source_manifest.csv",
}

MANIFEST_FIELDS = ["image_id", "source_url", "creator", "license", "attribution",
                   "capture_date", "location", "notes"]


def load_manifest_ids(manifest):
    if not manifest.exists():
        return set()
    with manifest.open(newline="") as f:
        return {row["image_id"] for row in csv.DictReader(f)}


def append_manifest(manifest, row):
    new_file = not manifest.exists() or manifest.stat().st_size == 0
    with manifest.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="config/experiment.json",
                   help="Config file with a \"download\" section (default: config/experiment.json)")
    p.add_argument("--spot", nargs=3, action="append", metavar=("NAME", "LAT", "LON"),
                   help="Spot to download; repeat for several. Replaces the spots in the config.")
    p.add_argument("--max-timestamps", type=int,
                   help="Max captures per spot, newest first, including the current one")
    p.add_argument("--zoom", type=int,
                   help="Resolution level: 3 = 4096x2048, 4 = 8192x4096, 5 = 16384x8192")
    p.add_argument("--outdir")
    p.add_argument("--manifest")
    p.add_argument("--overwrite", action="store_true", help="Re-download images that already exist")
    p.add_argument("--dry-run", action="store_true", help="List captures without downloading")
    args = p.parse_args()

    # Load the "download" section of the config (if the file exists)
    config_path = Path(args.config)
    cfg = {}
    if config_path.exists():
        cfg = json.loads(config_path.read_text()).get("download", {})
    elif args.config != p.get_default("config"):
        p.error(f"config file not found: {config_path}")

    # Command line > config file > fallback
    def setting(key):
        value = getattr(args, key)
        return value if value is not None else cfg.get(key, FALLBACKS[key])

    max_timestamps = setting("max_timestamps")
    zoom = setting("zoom")
    if max_timestamps < 1:
        p.error("max_timestamps must be at least 1")

    if args.spot:
        spots = {name: (float(lat), float(lon)) for name, lat, lon in args.spot}
    else:
        spots = {name: (float(lat), float(lon)) for name, (lat, lon) in cfg.get("spots", {}).items()}
    if not spots:
        p.error(f"no spots given: add them to \"download.spots\" in {config_path} or use --spot")

    print(f"Settings: {len(spots)} spot(s), max_timestamps={max_timestamps}, zoom={zoom}")
    outdir = Path(setting("outdir"))
    manifest = Path(setting("manifest"))
    if not args.dry_run:
        outdir.mkdir(parents=True, exist_ok=True)
    known_ids = load_manifest_ids(manifest)

    for name, (lat, lon) in spots.items():
        pano = streetview.find_panorama(lat, lon)
        if pano is None:
            print(f"{name}: no panorama found near {lat}, {lon}")
            continue

        # Newest first: the current panorama, then historical captures
        captures = [pano] + [streetview.find_panorama_by_id(h.id)
                             for h in pano.historical[:max_timestamps - 1]]
        print(f"{name}: {len(captures)} capture(s) (of {1 + len(pano.historical)} available)")

        for cap in captures:
            image_id = f"{name}_{cap.date}"
            path = outdir / f"{image_id}.jpg"
            print(f"   {cap.date}  {cap.id}  -> {path}")
            if args.dry_run:
                continue

            if path.exists() and not args.overwrite:
                print("      exists, skipping download")
            else:
                streetview.download_panorama(cap, str(path), zoom=zoom)

            if image_id not in known_ids:
                append_manifest(manifest, {
                    "image_id": image_id,
                    "source_url": cap.permalink(),
                    "creator": cap.uploader or "Google",
                    "license": "Google Maps/Street View Terms of Service (restricted; do not redistribute)",
                    "attribution": cap.copyright_message or "© Google",
                    "capture_date": str(cap.date),
                    "location": f"{cap.lat:.6f},{cap.lon:.6f}",
                    "notes": f"pano_id={cap.id}; spot={name}; zoom={zoom}",
                })
                known_ids.add(image_id)


if __name__ == "__main__":
    main()
