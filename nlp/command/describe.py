from nlp import describe_scene
from nlp.dispatch import Dispatchable


class DescribeScene(Dispatchable):

    def __init__(self, state_q):
        self.state_q = state_q

    def __call__(self, payload):
        state = self.state_q.get()

        if state:
            description = describe_scene(state)

            self.send({'response': description})


