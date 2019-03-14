import random
from abc import abstractmethod
from ..abstract import AbstractSoftware

class Software(AbstractSoftware):
    def setup(self):
        self.parse(self.config['path'])

    @abstractmethod
    def parse(self, path):
        self.contents = {}
        self.modification_points = {}

    @abstractmethod
    def synthetise(self, target):
        pass

    @abstractmethod
    def write(self, path):
        pass

    def random_target(self):
        target_file = random.choice(list(self.modification_points.keys()))
        target_point = random.choice(self.modification_points[target_file])
        return (target_file, target_point)

