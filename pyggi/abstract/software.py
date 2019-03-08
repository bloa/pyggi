from abc import ABC, abstractmethod
import re

class AbstractSoftware(ABC):
    def __init__(self, config=dict()):
        self.config = config

    @classmethod
    def from_file(cls, path):
        with open(path) as config_file:
            return cls(json.load(config_file))

    @abstractmethod
    def initial(self):
        pass

    def test(self, solution):
        return True

    @abstractmethod
    def run(self, solution):
        pass

    # TODO: better use JSON or YAML
    @staticmethod
    def parse(stdout, stderr):
        matched = re.findall(r"\[PYGGI_RESULT\]\s*\{(.*?)\}\s", stdout)
        if len(matched) == 0:
            return None
        custom = dict()
        for result in matched[0].split(','):
            assert len(result.split(':')) == 2
            # print("[Error] Result format is wrong!: {" + matched[0] + "}")
            key, value = result.split(':')[0].strip(), result.split(':')[1].strip()
            custom[key] = value
        return custom

    @staticmethod
    def hook_parse(output):
        return output
