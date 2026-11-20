"""Compare an original image with one or more method outputs using simple diagnostic statistics.

Metrics per output (all pixel-aligned, so sizes must match):
  - mean Lab shift (L, a, b) and warmth shift (b* + a*): how the colour moved
  - Canny edge F1 (edges within --tol px count as matching): structure preservation
  - SSIM on luminance: structural similarity
  - mean absolute luminance change and mean gradient-magnitude ratio (detail loss / added texture)

Usage:
  python src/evaluate.py --original data/crops/<id>/view_000.png --output outputs/baseline/<id>/view_000.png
  python src/evaluate.py --original data/crops/<id>/view_000.png \\
      --output outputs/baseline/<id>/view_000.png outputs/controlnet/<id>/view_000.png \\
      --labels Baseline ControlNet --csv outputs/eval.csv
"""
import argparse
import csv
import cv2
import numpy as np
from skimage.metrics import structural_similarity


def load(path):
    bgr = cv2.imread(str(path))
    if bgr is None:
        raise FileNotFoundError(path)
    return bgr


def mean_lab(bgr):
    # float conversion gives true CIELAB (L 0-100, a/b roughly -128..127)
    lab = cv2.cvtColor(bgr.astype(np.float32) / 255.0, cv2.COLOR_BGR2LAB)
    return lab.reshape(-1, 3).mean(axis=0)


def edges(bgr):
    return cv2.Canny(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY), 100, 200) > 0


def edge_f1(eo, en, tol):
    """Edge F1 where a pixel matches if the other map has an edge within `tol` pixels."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * tol + 1, 2 * tol + 1))
    near_o = cv2.dilate(eo.astype(np.uint8), k) > 0
    near_n = cv2.dilate(en.astype(np.uint8), k) > 0
    precision = np.count_nonzero(en & near_o) / max(1, np.count_nonzero(en))
    recall = np.count_nonzero(eo & near_n) / max(1, np.count_nonzero(eo))
    return 2 * precision * recall / max(1e-8, precision + recall)


def grad_mag(gray):
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    return np.sqrt(gx ** 2 + gy ** 2).mean()


def compare(orig, out, tol=1):
    if orig.shape != out.shape:
        raise ValueError(f'Input and output must have identical dimensions; got {orig.shape} vs {out.shape}')
    go = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
    gn = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
    lo, ln = mean_lab(orig), mean_lab(out)
    d = ln - lo
    return {
        'dL': d[0], 'da': d[1], 'db': d[2], 'warmth_shift': d[1] + d[2],
        'edge_f1_exact': edge_f1(edges(orig), edges(out), 0),
        f'edge_f1_tol{tol}': edge_f1(edges(orig), edges(out), tol),
        'ssim': structural_similarity(go, gn, data_range=255),
        'mean_abs_luma_change': float(np.abs(go.astype(np.float32) - gn.astype(np.float32)).mean()),
        'gradient_ratio': grad_mag(gn) / max(1e-6, grad_mag(go)),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--original', required=True)
    p.add_argument('--output', nargs='+', required=True, help='One or more method outputs')
    p.add_argument('--labels', nargs='+', help='One label per output (default: file path)')
    p.add_argument('--tol', type=int, default=1, help='Edge match tolerance in pixels (default 1)')
    p.add_argument('--csv', help='Also write results to this CSV')
    args = p.parse_args()
    labels = args.labels or args.output
    if len(labels) != len(args.output):
        p.error('provide one label per output')

    orig = load(args.original)
    print(f'Original Lab mean (CIELAB): {mean_lab(orig).round(2).tolist()}')
    rows = []
    for label, path in zip(labels, args.output):
        m = compare(orig, load(path), args.tol)
        rows.append({'method': label, 'path': path, **m})
        print(f'\n[{label}] {path}')
        for k, v in m.items():
            print(f'  {k:22s} {v: .3f}')
    if args.csv:
        with open(args.csv, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        print(f'\nSaved {args.csv}')
    print('\nNOTE: these are diagnostics, not proof of physically correct lighting or structural preservation.')
    print('Edge F1 and SSIM cannot tell a hallucinated object from a legitimate relighting change; inspect visually.')


if __name__ == '__main__':
    main()
