""" Repository of RCF detectors """

from .detector import Detector

class DetectorRepository:

    def __init__(self):
        self.repository = {}

    def get(self, uuid):
        if not uuid in self.repository:
            #TODO get detector metadata from model service
            metadata = {
                'cutoff_score': 1.72,
                'endpoint' : 'aa-rcf-1234-5678-test-2018-10-18T22-18-51-129293',
                'shingle_size' : 12
            }
            detector = Detector(metadata)
            self.add(uuid, detector)
        return self.repository[uuid]

    def add(self, uuid, detector):
        if not uuid in self.repository:
            self.repository[uuid] = detector

    def remove(self, uuid):
        del self.repository[uuid]

