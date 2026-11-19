"""Convert a 2:1 equirectangular panorama into six overlapping 90-degree perspective views.

Usage: python src/crop_panorama.py --input data/raw/site01_YYYY.png --outdir data/crops/site01_YYYY
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image
import py360convert


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True, help='2:1 panorama image path')
    p.add_argument('--outdir', required=True, help='Directory for output crops')
    p.add_argument('--size', type=int, default=512)
    args = p.parse_args()

    image = np.asarray(Image.open(args.input).convert('RGB'))
    height, width = image.shape[:2]
    if abs(width / height - 2) > 0.10:
        raise ValueError(f'Expected an approximately 2:1 equirectangular image; got {width}x{height}')

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for yaw in range(0, 360, 60):
        crop = py360convert.e2p(
            image, fov_deg=(90, 90), u_deg=yaw, v_deg=0,
            out_hw=(args.size, args.size), mode='bilinear',
        )
        path = outdir / f'view_{yaw:03d}.png'
        Image.fromarray(crop.astype(np.uint8)).save(path)
        print(path)
    print('Done: 6 perspective views. This covers a horizontal ring, not the full sphere.')


if __name__ == '__main__':
    main()
