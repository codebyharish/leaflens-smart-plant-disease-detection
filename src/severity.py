"""Transparent lesion-area screening heuristic.

It is deliberately presented as an approximate severity screen: accurate lesion
severity requires a separately labelled segmentation model, not class labels.
"""
from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def estimate_severity(image: Image.Image, is_healthy_prediction: bool) -> tuple[str, float, np.ndarray]:
    rgb = np.asarray(image.convert("RGB").resize((512, 512)))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    # Broad vegetation mask; rejects white/black background before measuring lesions.
    leaf = cv2.inRange(hsv, (20, 25, 20), (100, 255, 255))
    leaf = cv2.morphologyEx(leaf, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # Yellow/brown/dark patches may be disease, ageing, shadows, or damage.
    yellow_brown = cv2.inRange(hsv, (5, 35, 25), (38, 255, 235))
    dark = cv2.inRange(hsv, (0, 0, 10), (180, 120, 95))
    lesion = cv2.bitwise_and(cv2.bitwise_or(yellow_brown, dark), leaf)
    leaf_pixels = max(int(np.count_nonzero(leaf)), 1)
    pct = 0.0 if is_healthy_prediction else 100 * np.count_nonzero(lesion) / leaf_pixels
    if is_healthy_prediction:
        level = "No visible disease predicted"
    elif pct < 5:
        level = "Low"
    elif pct < 20:
        level = "Moderate"
    elif pct < 45:
        level = "High"
    else:
        level = "Critical"
    overlay = rgb.copy()
    overlay[lesion > 0] = (220, 50, 47)
    return level, float(min(pct, 100)), overlay
