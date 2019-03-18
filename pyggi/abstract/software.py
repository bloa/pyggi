from abc import ABC, abstractmethod
import re
from . import Patch

class AbstractSoftware(ABC):
    def __init__(self, config=dict()):
        self.config = config
        self.patch = Patch()
        self.setup()

    def setup(self):
        pass

    def apply(self, patch):
        self.patch = patch
        patch.alter(self)

    @classmethod
    def from_file(cls, path):
        with open(path) as config_file:
            return cls(json.load(config_file))

    def ready(self):
        pass

    def test(self, solution):
        return True

    @abstractmethod
    def run(self):
        pass
