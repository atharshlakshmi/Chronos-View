"""Stitching investigation: re-project the six horizon views onto a panorama band and blend the overlaps.

The six crops (90 deg FOV, one every 60 deg) overlap by 30 deg. This script
  1. measures how well neighbouring views agree inside their overlap (seam error, mean abs Lab difference),
  2. renders a hard-seam (nearest view wins) and a feather-blended panorama band.
Only the horizon band is covered (pitch 0, +/-45 deg vertical FOV at the view centres): this is NOT a full 360 output.
Seam error on the original crops is the floor; a method that relights each view independently
(e.g. diffusion) will usually score higher, a global colour grade should match the floor.

Usage: python src/seam_blend.py --views data/crops/<id> --output-dir outputs/seams/original_<id>
       python src/seam_blend.py --views outputs/baseline/<id> --output-dir outputs/seams/baseline_<id>
"""
import argparse
import csv
import json
from pathlib import Path
import cv2
import numpy as np

FOV = 90.0


def view_files(folder):
    files = sorted(Path(folder).glob('view_*.png'))
    if len(files) < 2:
        raise FileNotFoundError(f'need view_*.png files in {folder}')
    return [(int(f.stem.split('_')[1]), f) for f in files]


def sample(img, yaw, lon, lat):
    """Sample a pinhole view (given FOV, centred at yaw, pitch 0) at longitude/latitude (radians).
    Returns the sampled image and a validity weight (0 outside the view, rising to 1 at the centre)."""
    size = img.shape[0]
    f = (size / 2) / np.tan(np.radians(FOV / 2))
    dlon = lon - np.radians(yaw)
    dlon = (dlon + np.pi) % (2 * np.pi) - np.pi
    # direction in camera coords: z forward, x right, y down
    z = np.cos(lat) * np.cos(dlon)
    x = np.cos(lat) * np.sin(dlon)
    y = -np.sin(lat)
    ok = z > 1e-6
    u = np.where(ok, f * x / np.where(ok, z, 1) + size / 2, -1).astype(np.float32)
    v = np.where(ok, f * y / np.where(ok, z, 1) + size / 2, -1).astype(np.float32)
    out = cv2.remap(img, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    inside = (u >= 0) & (u <= size - 1) & (v >= 0) & (v <= size - 1)
    # feather: distance to the nearest image edge, normalised
    w = np.minimum(np.minimum(u, size - 1 - u), np.minimum(v, size - 1 - v)) / (size / 2)
    return out, np.where(inside, np.clip(w, 0, 1), 0).astype(np.float32)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--views', required=True, help='Folder with view_000.png ... view_300.png')
    p.add_argument('--output-dir', required=True)
    p.add_argument('--width', type=int, default=2048, help='Panorama band width in pixels (360 deg)')
    p.add_argument('--lat-range', type=float, default=35.0, help='Half height of the band in degrees (<= 45)')
    args = p.parse_args()

    views = [(yaw, cv2.imread(str(f)).astype(np.float32)) for yaw, f in view_files(args.views)]
    w = args.width
    h = int(round(w * 2 * args.lat_range / 360))
    lon = (np.arange(w, dtype=np.float32) + 0.5) / w * 2 * np.pi - np.pi
    lat = (0.5 - (np.arange(h, dtype=np.float32) + 0.5) / h) * np.radians(2 * args.lat_range)
    lon, lat = np.meshgrid(lon, lat)

    samples = [sample(img, yaw, lon, lat) for yaw, img in views]
    wsum = sum(s[1] for s in samples)
    blend = sum(s[0] * s[1][..., None] for s in samples) / np.maximum(wsum, 1e-6)[..., None]
    best = np.argmax(np.stack([s[1] for s in samples]), axis=0)
    hard = np.zeros_like(blend)
    for i, (img, _) in enumerate(samples):
        hard[best == i] = img[best == i]
    covered = wsum > 0
    blend[~covered] = 0

    # Seam error: neighbouring views compared inside their shared region (both weights > 0.05)
    def lab(a):
        return cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    errs, per_pair = [], {}
    for i in range(len(views)):
        j = (i + 1) % len(views)
        both = (samples[i][1] > 0.05) & (samples[j][1] > 0.05)
        if both.any():
            d = np.abs(lab(samples[i][0]) - lab(samples[j][0])).mean(axis=2)[both]
            per_pair[f'{views[i][0]:03d}-{views[j][0]:03d}'] = float(d.mean())
            errs.append(d)
    overall = float(np.concatenate(errs).mean()) if errs else float('nan')

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out / 'band_hard_seams.png'), np.clip(hard, 0, 255).astype(np.uint8))
    cv2.imwrite(str(out / 'band_feather_blend.png'), np.clip(blend, 0, 255).astype(np.uint8))
    report = {'views': args.views, 'band_size': [w, h], 'mean_overlap_lab_diff': overall,
              'per_pair_lab_diff': per_pair, 'covered_fraction': float(covered.mean()),
              'note': 'Horizon band only; not a full 360-degree output.'}
    (out / 'seam_report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f'Saved band images and seam_report.json to {out}')


if __name__ == '__main__':
    main()
