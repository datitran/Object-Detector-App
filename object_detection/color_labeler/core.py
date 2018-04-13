"""
Assigns a human understandable label to a color value


TODO: in python there's rarely a need for generic file or folder names like core.py or main.py
"""
from collections import OrderedDict
import pandas as pd
import numpy as np
import cv2

from object_detection.constants import COLOR_KEYS


def estimate_color(img, box=None):
    """

    Args:
        img: source RGB image
        box: bounding box (ymin, xmin, ymax, xmax)

    Returns:
        pd.Series: color histogram where the values are normalized pixel color frequencies

    Examples:
        >>> from skimage.data import coffee
        >>> estimate_color(coffee()).round(1)
        black     0.1
        white     0.3
        red       0.5
        orange    0.2
        yellow    0.0
        green     0.0
        cyan      0.0
        blue      0.0
        purple    0.0
        pink      0.0
        Name: color, dtype: float64
    """

    # Get center of image (via bounding box)
    cropped_img = _get_bbox_center_img(img, box)

    # Convert to Hue, Saturation, Value color space
    hsv_img = cv2.cvtColor(cropped_img, cv2.COLOR_RGB2HSV)

    # Flatten pixels in image
    flat_img = hsv_img.reshape((hsv_img.shape[0] * hsv_img.shape[1], 3))

    # Calculate indexed histograms of the Value dimension
    n_bins_val = 32
    black_bin_thresh = 5
    white_bin_thresh = 7

    bins_val = np.linspace(0, 255, n_bins_val, endpoint=True, dtype='uint8')
    hist_val_idx = np.digitize(flat_img[:, 2], bins_val)
    # hist_val, _ = np.histogram(hist_val_idx)

    is_black_pxl = hist_val_idx <= black_bin_thresh
    is_white_pxl = hist_val_idx >= (n_bins_val - white_bin_thresh)

    black_idx = hist_val_idx[is_black_pxl]
    white_idx = hist_val_idx[is_white_pxl]

    n_black = len(black_idx)
    n_white = len(white_idx)

    # Calculate histogram of Hue dimension
    color_flat_img = flat_img[~np.logical_or(is_black_pxl, is_white_pxl), :]  # exclude black or white pixels

    # Mathematical approach doesn't provide human understandable color ranges. Going to hardcode...
    # color_centers = np.arange(0, 360, 30)  # produces 12 color centers
    # color_ranges = (color_centers - 15) % 360  # maps to 360 deg bin ranges
    # bins_hue = color_ranges // 2  # ranges need to fit in uint8 space [0, 179]

    # [red, orange, yellow, green, cyan, blue, purple, pink]
    bins_hue = [-8, 7, 22, 37, 82, 97, 127, 142, 171]
    hist_hue, _ = np.histogram(color_flat_img[:, 0], bins=bins_hue)

    total = n_black + n_white + sum(hist_hue)

    return pd.Series([n_black, n_white] + list(hist_hue), index=COLOR_KEYS, name='color') / total


def _get_bbox_center_img(img, box=None):
    """

    Args:
        img:
        box:
    Examples:
        >>> from skimage.data import coffee
        >>> img = coffee()
        >>> cropped = _get_bbox_center_img(img)

    Returns:
        A cropped image around the center about half the original size

    """
    # get space measures
    if box is None:
        ymin, xmin, ymax, xmax = (0, 0, img.shape[0], img.shape[1])
    else:
        ymin, xmin, ymax, xmax = box

        if sum(box) <= 4:
            ymin = int(ymin * img.shape[0])
            ymax = int(ymax * img.shape[0])
            xmin = int(xmin * img.shape[1])
            xmax = int(xmax * img.shape[1])

    wd = xmax - xmin
    ht = ymax - ymin

    # Get center area of the object inside the bounding box
    ystart = ymin + (ht // 4)
    yend = ymax - (ht // 4)
    xstart = xmin + (wd // 4)
    xend = xmax - (wd // 4)

    obj_center = img[ystart:yend, xstart:xend, :]

    return obj_center
