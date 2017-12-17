""" State vector registration (consolidation/filtering over time in an intertial frame) and buffering """
import collections

import pandas as pd

from object_detection.constants import CATEGORY_INDEX


class SensorBuffer:
    """ Container for list lists of pairs containing information about images for past W frames (W = window width)

    Each object (vector) represents an instance ("the first person I saw today" not "person") in that video frame.
    zero or more vectors may be present for each video frame (image)
    [
      ['category', 'person'],
      ['instance', 1234567],  # this will be the same value across consecutive frames once object tracking is implemented
      ['x', .5], ['y', .25], ['z', 0.0],
      ['width', .12], ['height', .34], ['depth', 0],
      ['black', 7], ['white', 2],
      ['red', 5], ['blue', 10], ['yellow', 2],
      ['purple', 6], ['orange', 1], ['green', 1],
    ]
    -1 < x < 1 where 0 is the center of the frame, + 1 is far right
    -1 < y < 1 where 0 is center and +1 is the top of the frame
    z is TBD
    width and height are in the same scale as x, y, e.g. width = 2.0 / pixel_width
    depth units is TBD
    colors are pixel counts within a portion of the bounding box near the center
    """

    def __init__(self, samples=10, category_index=CATEGORY_INDEX):
        self.category_index = category_index

        # TODO: samples is actually 10 DataFrames each with up to N rows, where N is the maximum number of rows to be tracked
        if isinstance(samples, int):
            for i in range(samples):
                self.samples.append(pd.DataFrame())
        else:
            for i, row in enumerate(samples):
                # list of lists of dicts, lists, Series where each element is the "state" of a detected object
                self.samples += [pd.DataFrame()]
                for j, obj in enumerate(row):
                    self.samples[-1][j] = pd.Series(list(zip(*row))[1], index=list(zip(*row))[0], name=i)
                self.samples[-1].transpose(inplace=True)
        self.now = 0

    def update_state(self, boxes, classes, scores, category_index=None, window=10, max_boxes_to_draw=None, min_score_thresh=.4):
        """ Revise state based on latest frame of information (object boxes)

        Args:
            boxes (list): 2D numpy array of shape (N, 4): (ymin, xmin, ymax, xmax), in normalized format between [0, 1].
            classes,
        Args (thats hould be class attributes):
            category_index (dict of dicts): {1: {'id': 1, 'name': 'person'}, 2: {'id': 2, 'name': 'bicycle'},...}

        """
        category_index = self.category_index if category_index is None else category_index
        num_boxes = min([boxes.shape[0] if max_boxes_to_draw is None else max_boxes_to_draw,
                         boxes.shape[0], len(classes)])

        # FIXME: unify self.update_state.states with self.samples
        if self.update_state.states is None:
            # Initialize a matrix of state vectors for the past 20 frames
            self.update_state.row = 0
            self.update_state.window = 20
            self.update_state.columns = pd.DataFrame(
                list(self.category_index.values())).set_index('id', drop=True)['name']
            self.update_state.states = pd.DataFrame(pd.np.zeros((20, len(self.category_index)),
                                                                dtype=int), columns=self.update_state.columns)
            self.update_state.state0 = pd.Series(index=self.update_state.columns)

        state = []  # if state is None else state
        for i in range(num_boxes):
            if scores is None or scores[i] > min_score_thresh:
                # box = tuple(boxes[i].tolist())
                class_name = self.category_index.get(classes[i], {'name': 'unknown object'})['name']
                display_str = '{}: {} {}%'.format(classes[i], class_name, int(100 * scores[i]))
                print(display_str)
                state += [class_name]
        state = collections.Counter(state)
        # state = sorted(list(state.items()))

        # FIXME: not used
        self.update_state.states.iloc[self.update_state.row, :] = pd.Series(state)
        self.update_state.row = (self.update_state.row + 1) % len(self.update_state.states)  # update_state.window
        return state
    update_state.states = None


class Radar:
    """ Inertial 3D position of all objects detected over the course of a session """

    def __init__(self, category_index=CATEGORY_INDEX, category_names=10):
        pass

    def update(self, sensor_frame):
        """ Add or update all the objects listed in a sensor_frame vector to the radar map (inertial tracking of all objects). """
        pass
