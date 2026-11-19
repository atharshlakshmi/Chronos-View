"""Convert 2:1 equirectangular panoramas into overlapping perspective views.

By default, crops every image in data/raw/ into data/crops/<image_id>/view_000.png, view_060.png, ...
where <image_id> is the file name without its extension. Images that are already cropped are skipped.

Settings (input_dir, output_dir, size, fov_degrees, yaw_angles_degrees, pitch_degrees) are read from
the "crop" section of config/experiment.json. Command-line options override them.

Usage:
  python src/crop_panorama.py                     # crop everything in the input folder
  python src/crop_panorama.py --overwrite         # re-crop everything
  python src/crop_panorama.py --input data/raw/site01_YYYY.jpg   # one image
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
import py360convert

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Used when a setting is missing from both the command line and the config file
FALLBACKS = {
    "input_dir": "data/raw",
    "output_dir": "data/crops",
    "size": 512,
    "fov_degrees": 90,
    "yaw_angles_degrees": [0, 60, 120, 180, 240, 300],
    "pitch_degrees": 0,
}


def crop_one(input_path, outdir, size, fov, yaws, pitch):
    image = np.asarray(Image.open(input_path).convert('RGB'))
    height, width = image.shape[:2]
    if abs(width / height - 2) > 0.10:
        raise ValueError(f'Expected an approximately 2:1 equirectangular image; got {width}x{height}')

    outdir.mkdir(parents=True, exist_ok=True)
    for yaw in yaws:
        crop = py360convert.e2p(
            image, fov_deg=(fov, fov), u_deg=yaw, v_deg=pitch,
            out_hw=(size, size), mode='bilinear',
        )
        Image.fromarray(crop.astype(np.uint8)).save(outdir / f'view_{yaw:03d}.png')


def is_cropped(outdir, yaws):
    return all((outdir / f'view_{yaw:03d}.png').exists() for yaw in yaws)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--config', default='config/experiment.json',
                   help='Config file with a "crop" section (default: config/experiment.json)')
    p.add_argument('--input', help='Crop a single panorama instead of the whole input folder')
    p.add_argument('--input-dir', help='Folder of panoramas to crop')
    p.add_argument('--output-dir', help='Where <image_id>/ crop folders are created')
    p.add_argument('--size', type=int, help='Crop size in pixels (square)')
    p.add_argument('--overwrite', action='store_true', help='Re-crop images that already have crops')
    args = p.parse_args()

    # Load the "crop" section of the config (if the file exists)
    config_path = Path(args.config)
    cfg = {}
    if config_path.exists():
        cfg = json.loads(config_path.read_text()).get('crop', {})
    elif args.config != p.get_default('config'):
        p.error(f'config file not found: {config_path}')

    # Command line > config file > fallback
    def setting(key):
        value = getattr(args, key, None)
        return value if value is not None else cfg.get(key, FALLBACKS[key])

    size = setting('size')
    fov = setting('fov_degrees')
    yaws = [int(y) for y in setting('yaw_angles_degrees')]
    pitch = setting('pitch_degrees')
    input_dir = Path(setting('input_dir'))
    output_dir = Path(setting('output_dir'))

    if args.input:
        inputs = [Path(args.input)]
    else:
        inputs = sorted(f for f in input_dir.glob('*') if f.suffix.lower() in IMAGE_EXTENSIONS)
        if not inputs:
            p.error(f'no .jpg/.png images found in {input_dir}')

    print(f'Settings: {len(inputs)} image(s), size={size}, fov={fov}, yaws={yaws}, pitch={pitch}')
    done = skipped = failed = 0
    for input_path in inputs:
        outdir = output_dir / input_path.stem
        if is_cropped(outdir, yaws) and not args.overwrite:
            print(f'skip   {input_path.name} (already cropped)')
            skipped += 1
            continue
        try:
            crop_one(input_path, outdir, size, fov, yaws, pitch)
        except Exception as e:  # keep going so one bad image doesn't stop the batch
            print(f'FAILED {input_path.name}: {e}')
            failed += 1
            continue
        print(f'done   {input_path.name} -> {outdir}/')
        done += 1

    print(f'\n{done} cropped, {skipped} skipped, {failed} failed.')
    print(f'Each image gives {len(yaws)} views around the horizon, not the full sphere.')


if __name__ == '__main__':
    main()
