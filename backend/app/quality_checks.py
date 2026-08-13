import cv2
import numpy as np

BLUR_THRESHOLD = 100.0
MIN_BRIGHTNESS = 40
MAX_BRIGHTNESS = 220
MIN_FACE_SIZE_RATIO = 0.10


def run_quality_checks(image_bgr, bbox):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    x1, y1, x2, y2 = [int(v) for v in bbox]
    x1, y1 = max(0, x1), max(0, y1)
    face_crop = gray[y1:y2, x1:x2]

    issues = []

    blur_score = cv2.Laplacian(face_crop, cv2.CV_64F).var()
    if blur_score < BLUR_THRESHOLD:
        issues.append(f'Image too blurry (sharpness {blur_score:.1f}, need >= {BLUR_THRESHOLD})')

    brightness_score = float(np.mean(face_crop))
    if not (MIN_BRIGHTNESS <= brightness_score <= MAX_BRIGHTNESS):
        issues.append(f'Poor lighting (brightness {brightness_score:.1f}, need {MIN_BRIGHTNESS}-{MAX_BRIGHTNESS})')

    face_area = (x2 - x1) * (y2 - y1)
    image_area = image_bgr.shape[0] * image_bgr.shape[1]
    size_ratio = face_area / image_area if image_area > 0 else 0
    if size_ratio < MIN_FACE_SIZE_RATIO:
        issues.append(f'Face too small in frame ({size_ratio*100:.1f}% of image, need >= {MIN_FACE_SIZE_RATIO*100:.0f}%)')

    return {
        'passed': len(issues) == 0,
        'issues': issues,
        'blur_score': round(float(blur_score), 1),
        'brightness_score': round(brightness_score, 1),
        'face_size_ratio': round(size_ratio, 3),
    }
