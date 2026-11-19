"""Produce a comparison PNG of images, each with a label above it.

Usage: python src/contact_sheet.py --images input.png iclight.png controlnet.png baseline.png --labels Original IC-Light ControlNet Baseline --output outputs/comparison.png
"""
import argparse
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images', nargs='+', required=True)
    p.add_argument('--labels', nargs='+', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    if len(args.images) != len(args.labels):
        raise ValueError('Provide one label per image.')
    tile_size, pad, caption_h = 350, 12, 32
    canvas = Image.new('RGB', (len(args.images) * (tile_size + pad) + pad, tile_size + 2 * pad + caption_h), 'white')
    d = ImageDraw.Draw(canvas)
    for i, (image_path, label) in enumerate(zip(args.images, args.labels)):
        im = Image.open(image_path).convert('RGB')
        thumb = ImageOps.contain(im, (tile_size, tile_size))
        x = pad + i * (tile_size + pad)
        canvas.paste(thumb, (x + (tile_size - thumb.width) // 2, pad + caption_h + (tile_size - thumb.height)//2))
        d.text((x + 4, pad + 2), label, fill='black')
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    print(f'Saved {out}')


if __name__ == '__main__':
    main()
