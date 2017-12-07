""" State vector registration (consolidation/filtering over time in an intertial frame) and buffering """


class SensorBuffer:
    """ Container for list of dicts containing sensor samples for past W samples (W = window width) """

    def __init__(self, samples=10):
        if isinstance(samples, int):
            samples = []
            for i in range(samples):
                samples += [{}]
        self.samples = list(samples)
        self.now = 0


class Radar:
    """ Intertial 3D position of all objects detected over the course of a session """

    def __init__(self, category_names=10, category_names=10):
        if isinstance(states, int):
            sensor_frames = pd.DataFrame(pd.np.zeros((20, len(category_index)), dtype=int), columns=update_state.columns)
