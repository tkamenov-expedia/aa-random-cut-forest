""" RCF detector - one detector for one trained model. Keeps the history of metrics for each detector. """

from .shingle import Shingle

class Detector:

    def __init__(self, metadata):
        self.shingle = Shingle(12)
        self.metadata = metadata

    def new_metrics(self, value):
        self.shingle.push(value)

    def get_shingle(self):
        return self.shingle

    def get_metadata(self):
        return self.metadata

    # detector is not ready until shingle queue is full
    def is_ready(self):
        return self.shingle.is_ready()
