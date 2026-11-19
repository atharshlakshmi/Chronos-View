"""Fast no-diffusion warm-tone baseline preserving image geometry.

Usage: python src/color_grade.py --input data/crops/site01_YYYY/view_000.png --output outputs/baseline/view_000.png
"""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()

    im = Image.open(args.input).convert('RGB')
    rgb = np.asarray(im, dtype=np.float32)
    rgb *= np.array([1.06, 1.015, 0.91], dtype=np.float32)[None, None, :]
    rgb = np.uint8(np.clip(rgb, 0, 255))
    graded = ImageEnhance.Color(Image.fromarray(rgb)).enhance(1.06)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    graded.save(output)
    print(f'Saved {output}')


if __name__ == '__main__':
    main()
