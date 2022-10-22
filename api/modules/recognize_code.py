
from .cv_approach import cv_detector

# WILL BE MOVED TO FRONT-END LATER
__all__ = ['recognize_code']


def recognize_code(img, style_module: dict):
    """Recognize code pieces on the image and return the recognized code as a string"""
    return cv_detector(img, style_module)
