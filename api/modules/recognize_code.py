from .cv_approach import cv_detector
from .yolo_approach import yolo_detector

# WILL BE MOVED TO FRONT-END LATER
__all__ = ['recognize_code']


def recognize_code(img, style_module: dict):
    """Recognize code pieces on the image and return the recognized code as a string"""
    if style_module['object-detection-model']['supported']:
        return yolo_detector(img, style_module)
    return cv_detector(img, style_module)
