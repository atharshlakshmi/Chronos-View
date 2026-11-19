"""Compare two same-size images using simple diagnostic statistics.

Usage: python src/evaluate.py --original data/crops/site01_YYYY/view_000.png --output outputs/baseline/view_000.png
"""
import argparse
import cv2
import numpy as np


def summarize(path):
    bgr = cv2.imread(path)
    if bgr is None:
        raise FileNotFoundError(path)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    # OpenCV's 8-bit Lab uses L in [0,255], with a,b offset from 128.
    mean_lab = np.mean(lab, axis=(0, 1))
    edges = cv2.Canny(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), 100, 200) > 0
    return bgr, mean_lab, edges


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    orig, lo, eo = summarize(args.original)
    out, ln, en = summarize(args.output)
    if orig.shape != out.shape:
        raise ValueError('Input and output must have identical dimensions for evaluation.')
    intersection = np.count_nonzero(eo & en)
    precision = intersection / max(1, np.count_nonzero(en))
    recall = intersection / max(1, np.count_nonzero(eo))
    f1 = 2 * precision * recall / max(1e-8, precision + recall)
    print(f'Original Lab mean (OpenCV 8-bit): {lo.round(2).tolist()}')
    print(f'Output   Lab mean (OpenCV 8-bit): {ln.round(2).tolist()}')
    print(f'Pixel-aligned Canny edge F1: {f1:.3f}')
    print('NOTE: these are diagnostics, not proof of physically correct lighting or structural preservation.')


if __name__ == '__main__':
    main()
