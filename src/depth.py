"""Depth Anything V2 Small using the Hugging Face depth-estimation pipeline.

Usage: python src/depth.py --input data/crops/site01_YYYY/view_000.png --output data/depth/site01_YYYY/view_000.png
First install: python -m pip install -r requirements-depth.txt
"""
import argparse
from pathlib import Path
from PIL import Image
from transformers import pipeline


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()

    image = Image.open(args.input).convert('RGB')
    estimator = pipeline(task='depth-estimation', model='depth-anything/Depth-Anything-V2-Small-hf')
    predicted = estimator(image)
    # The pipeline returns a viewable normalized PIL depth image.
    depth_image = predicted['depth'].convert('RGB').resize(image.size, Image.Resampling.BILINEAR)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    depth_image.save(out)
    print(f'Saved visualized depth image: {out}')
    print('For quantitative depth analysis, also retain predicted_depth (raw tensor).')


if __name__ == '__main__':
    main()
