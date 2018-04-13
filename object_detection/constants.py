""" Constants that depend on the object detection model (tensorflow network) being used. """
import os
import numpy as np
import pandas as pd
from object_detection.utils import label_map_util


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Path to frozen detection graph. This is the actual model that is used for the object detection.
MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
LABEL_MAP_FILE = 'mscoco_label_map.pbtxt'
PATH_TO_CKPT = os.path.join(BASE_DIR, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(BASE_DIR, 'object_detection', 'data', LABEL_MAP_FILE)

# Loading label map
LABEL_MAP = label_map_util.load_labelmap(PATH_TO_LABELS)
# though mobilenet can handle
CATEGORIES = label_map_util.convert_label_map_to_categories(LABEL_MAP, max_num_classes=90, use_display_name=True)
CATEGORY_INDEX = label_map_util.create_category_index(CATEGORIES)

LABEL_KEYS = 'category instance confidence'.split()
COLOR_KEYS = 'black white red orange yellow green cyan blue purple pink'.split()
BB_KEYS = 'x y z width height depth'.split()
OBJECT_VECTOR_KEYS = LABEL_KEYS + BB_KEYS + COLOR_KEYS


class ObjectSeries(pd.Series):
    LABEL_KEYS = LABEL_KEYS
    COLOR_KEYS = COLOR_KEYS
    BB_KEYS = BB_KEYS
    OBJECT_VECTOR_KEYS = OBJECT_VECTOR_KEYS

    @property
    def obj_colors(self):
        return self[self.COLOR_KEYS]

    @property
    def obj_primary_color(self):
        return self.COLOR_KEYS[self.obj_colors.values.argmax()]

    @property
    def obj_labels(self):
        return self[self.LABEL_KEYS]

    @property
    def obj_bbox(self):
        return self[self.BB_KEYS]




