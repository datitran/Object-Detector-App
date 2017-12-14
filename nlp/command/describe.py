from nlp import describe_state
from nlp.dispatch import Dispatchable


class Describe(Dispatchable):

    def __init__(self, state_q):
        self.state_q = state_q

    def __call__(self, payload):
        state = self.state_q.get()

        if state:
            description = describe_state(state)

            self.send({'response': description}, subtopic=['say'])