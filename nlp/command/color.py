from nlp.dispatch import Dispatchable
import object_detection.constants as constants
from nlp.transform import position


class DescribeObjectColor(Dispatchable):

    color_tmpl = 'The {obj_name} is primarily {color}'
    color_fail_tmpl = 'I cannot determine the color'

    def __init__(self, state_q):
        self.state_q = state_q

    def __call__(self, payload):
        state = self.state_q.get()

        if state:

            if type(state[0]) is not constants.ObjectSeries:
                vecs = to_object_series_list(state)
            else:
                vecs = state

            center_vecs = list(filter(lambda v: position(v.obj_bbox) is 'center', vecs))

            if len(center_vecs) > 0:
                obj_vec = center_vecs.pop(0)
            else:
                obj_vec = vecs.pop(0)

            max_color = obj_vec.obj_primary_color
            obj_name = obj_vec['category']

            print(state)

            payload = {
                'response': self.color_tmpl.format(obj_name=obj_name, color=max_color)
            }

            self.send(payload)
            return

        payload = {
            'response': self.color_fail_tmpl
        }

        self.send(payload)


class DescribeSceneColor(Dispatchable):
    # TODO: implement

    def get_scene_color(self):
        pass


def to_object_series_list(state):
    return [constants.ObjectSeries(obj, index=constants.OBJECT_VECTOR_KEYS) for obj in state]

