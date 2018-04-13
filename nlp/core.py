""" Natural Language Processing (Generation) utilities """
import os
import typing

import pandas as pd
import object_detection.constants as constants

# fix the antipattern of having a separate folder for every function/class
from object_detection.color_labeler import estimate as estimate_color
from nlp.plurals import PLURALS
from collections import defaultdict
from nlp.transform import position, estimate_distance

from collections import Counter



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
            [
                ['cup', 0, .95, -.5, .1, 0, .1, .1, 0, .5, .3, .14, .01, .01, .01, .01, .01, .01, .01]
                ['ski', 0, .80, -.5, .1, 0, .1, .1, 0, .5, .3, .14, .01, .01, .01, .01, .01, .01, .01]
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
            # change variable name later

            object_vectors.append([class_name, 0, scores[i]] + list(estimate_distance(boxes[i])) +
                                  list(estimate_color(image, box=boxes[i])))
    return object_vectors


def describe_scene(object_vectors):
    """ Convert a state vector dictionary of objects and their counts into a natural language string

            categ inst,  conf, x   y  z  wdth hght dpth blk wht red orng  yel  grn  cyn  blu purp pink
    >>> object_vectors = [
    ...    ['cup', 0,   .95, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01],
    ...    ['ski', 0,   .80, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01]
    ... ]
    >>> desc = describe_scene(object_vectors)
    >>> 'a black cup' in desc and ' and ' in desc and 'a black ski' in desc
    True
    """
    feature_list = list(map(object_features, object_vectors))

    plural_descriptions = aggregate_descriptions_by_features(feature_list)

    delim_description = compose_comma_series(plural_descriptions)

    return delim_description


def aggregate_descriptions_by_features(feature_list, *,
                                       include_color: bool = True, include_position: bool = True) -> typing.List[str]:
    """Produce a list of descriptions created through aggregations (counts) of objects in the scene.

    Can optionally aggregate by color and position.

    Args:
        feature_list: list of tuples with description features [(<category name>, <color>, <position>), ...]
        include_color: flag to aggregate by color
        include_position: flag to aggregate by position

    Returns:
        A list of strings with valid descriptions.

    Examples:
        TODO(Hobbs, Ashwin): Please review these test cases
        >>> obj_vectors = [
        ...    ['cup', 0,   .95, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01],
        ...    ['cup', 0,   .95, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01],
        ...    ['ski', 0,   .80, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01]
        ... ]
        >>> feature_list = list(map(object_features, obj_vectors))
        >>> descs = aggregate_descriptions_by_features(feature_list)
        >>> '2 black cups to your left' in descs and 'a black ski to your left' in descs
        True
        >>> no_color = aggregate_descriptions_by_features(feature_list, include_color=False)
        >>> '2 cups to your left' in no_color and 'a ski to your left' in no_color
        True
        >>> obj_vectors_color = [
        ...    ['cup', 0,   .95, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .51, .01, .01, .01, .01, .01, .01],
        ...    ['cup', 0,   .95, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01],
        ...    ['ski', 0,   .80, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01]
        ... ]
        >>> feature_list = list(map(object_features, obj_vectors_color))
        >>> diff_colors = aggregate_descriptions_by_features(feature_list)
        >>> 'an orange cup to your left' in diff_colors and 'a black cup to your left' in diff_colors
        True
        >>> diff_no_colors = aggregate_descriptions_by_features(feature_list, include_color=False)
        >>> '2 cups to your left' in diff_no_colors
        True
        >>> obj_vectors_pos = [
        ...    ['cup', 0,   .95, 0.7, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01],
        ...    ['cup', 0,   .95, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01],
        ...    ['ski', 0,   .80, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01]
        ... ]
        >>> feature_list = list(map(object_features, obj_vectors_pos))
        >>> diff_pos = aggregate_descriptions_by_features(feature_list)
        >>> 'a black cup to your left' in diff_pos and 'a black cup to your right' in diff_pos
        True
        >>> diff_no_pos = aggregate_descriptions_by_features(feature_list, include_position=False)
        >>> '2 black cups' in diff_no_pos
        True
    """

    def include_features(f):
        """Filters feature tuple s.t. we include only the features we want to aggregate over. """
        assert len(f) == 3, 'Make sure to include all the features in this function!!'

        fs = list()
        fs.append(f[0])

        if include_color:
            fs.append(f[1])

        if include_position:
            fs.append(f[2])

        return tuple(fs)

    included = list(map(include_features, feature_list))

    counts = Counter(included)

    pluralized_feature_groups = [describe_object_from_feature(feature, count,
                                                               include_color=include_color,
                                                               include_position=include_position)
                                  for feature, count in counts.items()]

    return pluralized_feature_groups


def describe_object(obj_vec) -> str:
    """Creates formatted string description from object vector

    Args:
        obj_vec: a vector representing a single object.

    Returns:
        a description of the object.

    Examples:

        >>> obj_vec = ['cup', 0,   .95, -.5, .1, 0,  .1,  .1,  0,  .5, .3, .14, .01, .01, .01, .01, .01, .01, .01]
        >>> describe_object(obj_vec)
        'a black cup to your left'
    """
    feature = object_features(obj_vec)
    return describe_object_from_feature(feature)


def describe_object_from_feature(feature, count: typing.Optional[int] = None, *,
                                 include_color: bool = True, include_position: bool = True) -> str:
    """Creates formatted string description from object features and counts, including pluralization.

    Args:
        feature: tuple of strings (<category name>, <color>)
        count: a count of the occurrence of the feature, or None
        include_color: Optionally include the color feature in description
        include_position: Optionally include the position in object description

    Returns:
        A noun phrase describing the object.

    Raises:
        - AssertionError: This is for development time. Should the feature tuple get more than
            the expected number of items in the tuple, an assertion error should be thrown
        - ValueError: Count cannot be zero, negative, or an non-integer less than 1.

    Examples:
        >>> describe_object_from_feature(('cup', 'white', 'left'))
        'a white cup to your left'
        >>> describe_object_from_feature(('cup', 'orange', 'center'))
        'an orange cup to your center'
        >>> describe_object_from_feature(('cup', 'red', 'right'), 2)
        '2 red cups to your right'

    """
    name, *rest = feature

    if include_color:
        color, *rest = rest
    else:
        color = None

    if include_position:
        position, *rest = rest
    else:
        position = None

    assert len(rest) == 0, 'Need to update string formatting function with new features!'

    if count is None:
        count = 1

    # Structure the string templates based on what features to include
    base_tmpl = '{name}'
    multiple_desc_tmpl = base_tmpl
    single_desc_tmlp = base_tmpl

    if include_color:
        multiple_desc_tmpl = '{color} ' + multiple_desc_tmpl
        single_desc_tmlp = '{color} ' + single_desc_tmlp

    if include_position:
        multiple_desc_tmpl += ' to your {position}'
        single_desc_tmlp += ' to your {position}'

    multiple_desc_tmpl = '{amount} ' + multiple_desc_tmpl
    single_desc_tmlp = '{article} ' + single_desc_tmlp

    if count > 1:
        output = multiple_desc_tmpl.format(amount=count,
                                           color=color,
                                           name=pluralize(name),
                                           position=position)
    elif count == 1:
        first_word = color if include_color else name
        article = 'an' if _starts_with_vowel(first_word) else 'a'

        output = single_desc_tmlp.format(article=article,
                                         color=color,
                                         name=name,
                                         position=position)
    else:
        raise ValueError('There cannot be zero, negative, or fractional objects!')

    return output


def _starts_with_vowel(char) -> bool:
    """Test to see if string starts with a vowel

    Args:
        char: character or string

    Returns:
        bool True if the character is a vowel, False otherwise

    Examples:
        >>> _starts_with_vowel('a')
        True
        >>> _starts_with_vowel('b')
        False
        >>> _starts_with_vowel('cat')
        False
        >>> _starts_with_vowel('apple')
        True
    """
    if len(char) > 1:
        char = char[0]

    return char in 'aeiou'


def object_features(obj_vec):
    """Converts object vector to a tuple of labels (name, color, position, etc.)

    Args:
        obj_vec:

    Returns:
        Tuple of strings with the following format:
        (<cateogry name>, <color>, ...)

    Examples:
        >>> obj_vec = ['cup', 0, .95, -.5, .1, 0, .1, .1, 0, .5, .3, .14, .01, .01, .01, .01, .01, .01, .01]
        >>> object_features(obj_vec)
        ('cup', 'black', 'left')
    """
    if type(obj_vec) is list or type(obj_vec) is pd.Series:
        obj_vec = constants.ObjectSeries(obj_vec, index=constants.ObjectSeries.OBJECT_VECTOR_KEYS)

    #       Name,                Color,                    Position
    return obj_vec['category'], obj_vec.obj_primary_color, position(tuple(obj_vec.obj_bbox))


def compose_comma_series(noun_list: typing.List[str]) -> str:
    """ Join a list of noun phrases into a comma delimited series

    Args:
        noun_list: list of noun phrases (object + adjective descriptors)

    Returns:
        string consisting of a comma delimited series of noun phrases

    Examples:
        >>> compose_comma_series(['1 pair of skis', '2 cups'])
        '1 pair of skis and 2 cups'
        >>> compose_comma_series(['1 pair of skis', '2 cups', '1 laptop'])
        '1 pair of skis, 2 cups and 1 laptop'
    """
    comma_list = ', '.join(noun_list[:-2])
    conjunction = ' and '.join(noun_list[-2:])

    if len(comma_list) > 0:
        delim_description = comma_list + ', ' + conjunction
    else:
        delim_description = conjunction

    return delim_description


def say(s, rate=250):
    """ Convert text to speech (TTS) and play resulting audio to speakers

    If "say" command is not available in os.system then print the text to stdout and return False.

    >>> result = say('hello')  # TODO(Ashwin | Alex | Hobbs) This test will fail on Jenkins
    >>> result == 'hello' or result == False
    True
    """
    shell_cmd = 'say --rate={rate} "{s}"'.format(**dict(rate=rate, s=s))
    try:
        status = os.system(shell_cmd)
        if status > 0:
            print('os.system({shell_cmd}) returned nonzero status: {status}'.format(**locals()))
            raise OSError
        return s
    except OSError:
        print(s)
    return False
