
import cv2
import numpy as np


# ==========================================
# FORGESIGHT - HEAT PUMPING DETECTOR
# ==========================================

GREEN_LOWER = np.array([30, 55, 65], dtype=np.uint8)
GREEN_UPPER = np.array([90, 255, 255], dtype=np.uint8)

PROCESS_SCALE = 0.5
MINIMUM_AREA = 100
MINIMUM_CIRCULARITY = 0.45

# Only inspect the leftmost 30% of the Roblox client.
ROI_WIDTH_RATIO = 0.30


def detect_green_target(frame):

    if frame is None:
        return None

    rgb = np.asarray(frame.convert("RGB"))

    original_height, original_width = rgb.shape[:2]

    # ======================================
    # REGION OF INTEREST
    # ======================================

    roi_width = max(
        1,
        int(original_width * ROI_WIDTH_RATIO)
    )

    roi = rgb[:, :roi_width]

    # ======================================
    # IMAGE PROCESSING
    # ======================================

    small = cv2.resize(
        roi,
        None,
        fx=PROCESS_SCALE,
        fy=PROCESS_SCALE,
        interpolation=cv2.INTER_AREA
    )

    hsv = cv2.cvtColor(
        small,
        cv2.COLOR_RGB2HSV
    )

    mask = cv2.inRange(
        hsv,
        GREEN_LOWER,
        GREEN_UPPER
    )

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # ======================================
    # CANDIDATE DETECTION
    # ======================================

    candidates = []

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < MINIMUM_AREA:
            continue

        perimeter = cv2.arcLength(
            contour,
            True
        )

        if perimeter <= 0:
            continue

        circularity = (
            4.0 * np.pi * area
            / (perimeter * perimeter)
        )

        if circularity < MINIMUM_CIRCULARITY:
            continue

        x, y, width, height = cv2.boundingRect(contour)

        if height == 0:
            continue

        aspect_ratio = width / height

        if not 0.65 <= aspect_ratio <= 1.45:
            continue

        region = mask[
            y:y + height,
            x:x + width
        ]

        green_ratio = (
            cv2.countNonZero(region)
            / (width * height)
        )

        if green_ratio < 0.35:
            continue

        score = area * circularity * green_ratio

        candidates.append({
            "box": (x, y, width, height),
            "score": score
        })

    if not candidates:
        return None

    # ======================================
    # SELECT BEST CANDIDATE
    # ======================================

    best = max(
        candidates,
        key=lambda item: item["score"]
    )

    x, y, width, height = best["box"]

    # ======================================
    # RESTORE ORIGINAL COORDINATES
    # ======================================

    inverse_scale = 1.0 / PROCESS_SCALE

    x = round(x * inverse_scale)
    y = round(y * inverse_scale)
    width = round(width * inverse_scale)
    height = round(height * inverse_scale)

    # Coordinates are already relative to the
    # full Roblox frame because the ROI starts at x=0.

    x = max(0, min(x, roi_width - 1))
    y = max(0, min(y, original_height - 1))

    width = min(width, roi_width - x)
    height = min(height, original_height - y)

    return {
        "box": (x, y, width, height),
        "center": (
            x + width // 2,
            y + height // 2
        )
    }
