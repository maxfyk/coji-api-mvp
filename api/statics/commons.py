import os
import base64
import io
import cv2
import numpy as np
from runpy import run_path

from statics.constants import STYLES_PATH_FULL


def string_img_to_cv2(image_bytes: bytes):
    """Return CV2 image"""
    try:
        img = io.BytesIO(base64.b64decode(image_bytes))
        img = np.frombuffer(img.read(), dtype=np.uint8)
        img = cv2.imdecode(img, flags=1)
    except Exception as e:
        return None
    return img


def get_style_info(style_name: str):
    return run_path(os.path.join(STYLES_PATH_FULL.format(style_name), 'properties.py'))['style_module']
