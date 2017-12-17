""" Natural Language Processing (Generation) utilities """
import collections
import os

import pandas as pd
# fix the antipattern of having a separate folder for every function/class
from object_detection.color_labeler import estimate as estimate_color

from nlp.plurals import PLURALS
from collections import defaultdict


def pluralize(s):
    """ Convert word to its plural form.

    >>> pluralize('cat')
    'cats'
    >>> pluralize('doggy')
    'doggies'

    Better:

    >> from pattern.en import pluralize, singularize

    Or, even better, just create pluralized versions of all the class names by hand!
    """
    word = str.lower(s)

    # `.get()` rather than `word in PLURALS` so that we only look up the word once
    pluralized_word = PLURALS.get(word, None)
    if pluralized_word is not None:
        return pluralized_word

    # case = str.lower(s[-1]) == s[-1]
    if word.endswith('y'):
        if word.endswith('ey'):
            return word + 's'
        else:
            return word[:-1] + 'ies'
    elif word[-1] in 'sx' or word[-2:] in ['sh', 'ch']:
        return word + 'es'
    elif word.endswith('an') and len(word) > 3:
        return word[:-2] + 'en'
    else:
        return word + 's'


def update_state(image, boxes, classes, scores, category_index, window=10, max_boxes_to_draw=None, min_score_thresh=.5):
    """ Revise state based on latest frame of information (object boxes)

    TODO: complete docstring

    Args:
        boxes (list): 2D numpy array of shape (N, 4): (ymin, xmin, ymax, xmax), in normalized format between [0, 1].
        classes,
    Args (that should be class attributes):
        category_index (dict of dicts): {1: {'id': 1, 'name': 'person'}, 2: {'id': 2, 'name': 'bicycle'},...}
    Returns:
        list: list of object vectors, for example:
        LABEL_KEYS = '.split()
            [
                ['cup', 0, .95, -.5, .1, 0, .1, .1, 0, .5, .3, .14, .01, .01, .01, .01, .01, .01]
                ['ski', 0, .80, -.5, .1, 0, .1, .1, 0, .5, .3, .14, .01, .01, .01, .01, .01, .01]
            ]
            The object vector keys are defined in constants.OBJECT_VECTOR_KEYS:
                [category instance confidence x y z width height depth
                 black white red orange yellow green cyan blue purple pink]
    """
    num_boxes = min([boxes.shape[0] if max_boxes_to_draw is None else max_boxes_to_draw, boxes.shape[0], len(classes)])

    object_vectors = []
    for i in range(num_boxes):
        if scores is None or scores[i] > min_score_thresh:
            # box = tuple(boxes[i].tolist())
            class_name = category_index.get(classes[i], {'name': 'unknown object'})['name']
            display_str = '{}: {} {}%'.format(classes[i], class_name, int(100 * scores[i]))
            print(display_str)  # TODO: Convert to logging
            object_vectors.append([class_name, 0, scores[i], 0, 0, 0, 0, 0, 0] +
                                  list(estimate_color(image, box=boxes[i])))
    return object_vectors


def describe_scene(object_vectors):
    """ Convert a state vector dictionary of objects and their counts into a natural language string

    >>> describe_scene({'skis': [{'score': 0.99}, {'score': 0.88}]})
    '2 pairs of skis'
    >>> object_vectors = [
    ...    ['cup', 0, .95, -.5, .1, 0, .1, .1, 0, .5, .3, .14, .01, .01, .01, .01, .01, .01]
    ...    ['ski', 0, .80, -.5, .1, 0, .1, .1, 0, .5, .3, .14, .01, .01, .01, .01, .01, .01]
    ... ]
    >>> describe_scene(object_vectors)
    """
    def count_objects(object_vectors):
        return collections.Counter(list(zip(*object_vectors))[0]) if len(object_vectors) else {}

    object_counts = count_objects(object_vectors)

    plural_description_list = ['{} {}'.format(i, pluralize(s) if i > 1 else s) for (s, i) in object_counts.items()]

    comma_list = ', '.join(plural_description_list[:-2])
    conjunction = ' and '.join(plural_description_list[-2:])
    if len(comma_list) > 0:
        delim_description = comma_list + ',' + conjunction
    else:
        delim_description = conjunction

    return delim_description


def say(s, rate=230):
    """ Convert text to speech (TTS) and play resulting audio to speakers

    If "say" command is not available in os.system then print the text to stdout and return False.

    >>> say('hello')
    'hello'
    """
    try:
        os.system('say --rate={rate} "{s}"'.format(**dict(rate=rate, s=s)))
        return s
    except:
        print(s)
    return False
