""" Natural Language Processing (Generation) utilities """
import collections
import os

import pandas as pd


PLURALS = {
    'apple': 'apples',
    'backpack': 'backpacks',
    'ball': 'balls',
    'banana': 'bananas',
    'baseball bat': 'baseball bats',
    'baseball glove': 'baseball gloves',
    'bear': 'bears',
    'bed': 'beds',
    'bench': 'benches',
    'bicycle': 'bicycles',
    'bird': 'birds',
    'boat': 'boats',
    'book': 'books',
    'bottle': 'bottles',
    'bowl': 'bowls',
    'broccoli': 'broccoli bunches',
    'bus': 'busses',
    'cake': 'cakes',
    'car': 'cars',
    'carrot': 'carrots',
    'cat': 'cats',
    'chair': 'chairs',
    'clock': 'clocks',
    'couch': 'couches',
    'cow': 'cows',
    'cup': 'cups',
    'dining table': 'dining tables',
    'dog': 'dogs',
    'donut': 'donuts',
    'elephant': 'elephants',
    'fire hydrant': 'fire hydrants',
    'fork': 'forks',
    'frisbee': 'frisbees',
    'giraffe': 'giraffes',
    'hair drier': 'hair driers',
    'handbag': 'handbags',
    'horse': 'horses',
    'hot dog': 'hot dogs',
    'keyboard': 'keyboards',
    'kite': 'kites',
    'knife': 'knives',
    'laptop': 'laptops',
    'microwave': 'microwave ovens',
    'mobile phone': 'mobile phones',
    'monitor': 'monitors',
    'motorcycle': 'motorcycles',
    'mouse': 'mice',
    'orange': 'oranges',
    'oven': 'ovens',
    'parking meter': 'parking meters',
    'person': 'people',
    'pizza': 'pizzas',
    'plane': 'planes',
    'potted plant': 'potted plants',
    'refrigerator': 'refrigerators',
    'remote': 'remotes',
    'sandwich': 'sandwiches',
    'scissors': 'pairs of scissors',
    'sheep': 'sheep',
    'sink': 'sinks',
    'skateboard': 'skateboards',
    'skis': 'pairs of skis',
    'snowboard': 'snowboards',
    'spoon': 'spoons',
    'stop sign': 'stop signs',
    'suitcase': 'suitcases',
    'surfboard': 'surfboards',
    'teddy bear': 'teddy bears',
    'tennis racket': 'tennis rackets',
    'tie': 'ties',
    'toaster': 'toasters',
    'toilet': 'toilets',
    'toothbrush': 'toothbrushes',
    'traffic light': 'traffic lights',
    'train': 'trains',
    'truck': 'trucks',
    'umbrella': 'umbrellas',
    'vase': 'vases',
    'wine glass': 'wine glasses',
    'zebra': 'zebras'}


def pluralize(s):
    """ Convert word to its plural form.

    >>> pluralize('cat')
    cats
    >>> pluralize('doggy')
    doggies

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


def update_state(boxes, classes, scores, category_index, window=10, max_boxes_to_draw=None, min_score_thresh=.5):
    """ Revise state based on latest frame of information (object boxes)

    Args:
        boxes (list): 2D numpy array of shape (N, 4): (ymin, xmin, ymax, xmax), in normalized format between [0, 1].
        classes,
    Args (that should be class attributes):
        category_index (dict of dicts): {1: {'id': 1, 'name': 'person'}, 2: {'id': 2, 'name': 'bicycle'},...}

    """
    num_boxes = min([boxes.shape[0] if max_boxes_to_draw is None else max_boxes_to_draw, boxes.shape[0], len(classes)])

    if update_state.states is None:
        # Initialize a matrix of state vectors for the past 20 frames
        update_state.i = 0
        update_state.window = 20
        update_state.columns = pd.DataFrame(list(category_index.values())).set_index('id', drop=True)['name']
        update_state.states = pd.DataFrame(pd.np.zeros((20, len(category_index)), dtype=int), columns=update_state.columns)
        update_state.state0 = pd.Series(index=update_state.columns)

    state = []  # if state is None else state
    for i in range(num_boxes):
        if scores is None or scores[i] > min_score_thresh:
            # box = tuple(boxes[i].tolist())
            class_name = category_index.get(classes[i], {'name': 'unknown object'})['name']
            display_str = '{}: {} {}%'.format(classes[i], class_name, int(100 * scores[i]))
            print(display_str)
            state += [class_name]
    state = collections.Counter(state)
    update_state.states.iloc[i % len(update_state.states), :] = pd.Series(state)
    state = sorted(list(state.items()))
    i = (i + 1) % len(update_state.states)  # update_state.window
    return state


update_state.states = None

# for i in range(update_state.window):
#     update_state.states.append([])


def describe_state(state):
    """ Convert a state vector dictionary of objects and their counts into a natural language string

    >>> describe_state({'skis': 2})
    '2 pairs of skis'
    """
    description = ['{} {}'.format(i, pluralize(s) if i > 1 else s) for (s, i) in state]
    description = ', '.join(description[:-2]) + ',' + ' and '.join(description[-2:])
    return description


def say(s, rate=230):
    """ Convert text to speech (TTS) and play resulting audio to speakers

    If "say" command is not available in os.system then print the text to stdout.

    >>> say(hello)
    'hello'
    """
    try:
        os.system('say --rate={rate} "{s}"'.format(**dict(rate=rate, s=s)))
        return s
    except:
        print(s)
    return False
