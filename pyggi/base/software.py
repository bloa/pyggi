from abc import ABC, abstractmethod
import os
import random
import re
import shlex
import shutil
import subprocess
import time
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


class Software(AbstractSoftware):
    def setup(self):
        self.parse(self.config['path'])
        if not 'timeout' in self.config:
            self.config['timeout'] = None
        self.path = './pyggi_tmp'

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

    def ready(self):
        assert(self.path != self.config['path'])
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        shutil.copytree(self.config['path'], self.path) # for unmanaged files
        self.write(self.path)

    def test(self):
        if 'test_cmd' in self.config:
            return self.exec_cmd(self.config['test_cmd'])
        else:
            return True

    def run(self):
        return self.exec_cmd(self.config['run_cmd'], self.config['timeout'])

    def exec_cmd(self, cmd, timeout):
        cwd = os.getcwd()
        try:
            os.chdir(self.path)
            sprocess = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                stdout, stderr = sprocess.communicate(timeout=timeout)
                output = self.parse_output(stdout.decode("ascii"), stderr.decode("ascii"))
            except subprocess.TimeoutExpired:
                return None
        finally:
            os.chdir(cwd)
        return output

    # TODO: better use JSON or YAML
    @staticmethod
    def parse_output(stdout, stderr):
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
    def hook_parse_output(output):
        return output

    def random_target(self):
        target_file = random.choice(list(self.modification_points.keys()))
        target_point = random.choice(self.modification_points[target_file])
        return (target_file, target_point)

