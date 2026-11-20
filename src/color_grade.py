"""Fast no-diffusion warm-tone baseline preserving image geometry.

Applies a fixed per-channel warm gain plus a mild saturation boost. Because the same global
transform is applied to every pixel, geometry is untouched and adjacent views stay consistent.

Usage:
  # one image
  python src/color_grade.py --input data/crops/<image_id>/view_000.png --output outputs/baseline/<image_id>/view_000.png
  # all views of one image ID (view_*.png)
  python src/color_grade.py --input-dir data/crops/<image_id> --output-dir outputs/baseline/<image_id>
Add --log to append a row per image to docs/experiment_log.csv.
"""
import argparse
import csv
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance

GAINS = (1.06, 1.015, 0.91)   # R, G, B multipliers (warm shift)
SATURATION = 1.06
LOG_FIELDS = ['image_id', 'view', 'method', 'model_version', 'prompt', 'seed', 'denoising_strength',
              'controlnet_scale', 'device', 'result_path', 'notes']


def grade(im, gains=GAINS, saturation=SATURATION):
    rgb = np.asarray(im.convert('RGB'), dtype=np.float32) * np.array(gains, dtype=np.float32)[None, None, :]
    graded = Image.fromarray(np.uint8(np.clip(rgb, 0, 255)))
    return ImageEnhance.Color(graded).enhance(saturation)


def log_row(log_path, input_path, output_path):
    log_path = Path(log_path)
    new = not log_path.exists() or log_path.stat().st_size == 0
    with log_path.open('a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow({
            'image_id': input_path.parent.name, 'view': input_path.stem, 'method': 'color_grade_baseline',
            'model_version': 'none', 'prompt': 'n/a', 'seed': 'n/a', 'denoising_strength': 'n/a',
            'controlnet_scale': 'n/a', 'device': 'cpu', 'result_path': str(output_path),
            'notes': f'RGB gains={GAINS}; saturation={SATURATION}',
        })


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--input', help='Single input image')
    p.add_argument('--output', help='Output path for --input')
    p.add_argument('--input-dir', help='Folder of view_*.png to grade')
    p.add_argument('--output-dir', help='Output folder for --input-dir')
    p.add_argument('--log', action='store_true', help='Append rows to docs/experiment_log.csv')
    args = p.parse_args()

    if args.input and args.output:
        pairs = [(Path(args.input), Path(args.output))]
    elif args.input_dir and args.output_dir:
        files = sorted(Path(args.input_dir).glob('view_*.png'))
        if not files:
            p.error(f'no view_*.png in {args.input_dir}')
        pairs = [(f, Path(args.output_dir) / f.name) for f in files]
    else:
        p.error('give --input and --output, or --input-dir and --output-dir')

    for src, dst in pairs:
        dst.parent.mkdir(parents=True, exist_ok=True)
        grade(Image.open(src)).save(dst)
        print(f'Saved {dst}')
        if args.log:
            log_row('docs/experiment_log.csv', src, dst)


if __name__ == '__main__':
    main()
