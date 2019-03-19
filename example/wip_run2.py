import copy
import random
import time
from pyggi.base import Patch
from pyggi.algorithms import IteratedLocalSearch
from pyggi.tree import TreeDeletion, TreeReplacement
from pyggi.tree import AstorProgram

class MyProgram(AstorProgram):
    def setup(self):
        super().setup()
        self.config['timeout'] = 1

    def parse_output(self, stdout, stderr):
        return stderr == ''

    def run(self):
        start = time.time()
        if super().run():
            return time.time() - start
        return None

EDITS = [TreeDeletion, TreeReplacement]

class MyAlgo(IteratedLocalSearch):
    def stopping_condition(self):
        return self.stats['steps'] >= 30

    def neighbourhood(self, sol):
        for _ in range(100): # neighbourhood size
            c = copy.deepcopy(sol)
            yield self.mutate(c)

    def mutate(self, sol):
        if len(sol) > 1 and random.random() > 0.5:
            sol.edits.pop(int(random.random()*len(sol)))
        else:
            sol.edits.append(random.choice(EDITS).create(self.software))
        return sol

if __name__ == "__main__":
    config = {
        'path': '.',
        'target_files': ['wip_abstract.py'],
        'run_cmd': 'python wip_abstract.py',
    }

    software = MyProgram(config)
    algo = MyAlgo(software)
    algo.run()

    print()
    print('===== Finish =====')
    print('best fitness:', algo.fitness(algo.best))
    print(algo.best)
    print()
    soft = copy.deepcopy(software)
    algo.best.alter(soft)
    soft.write('pyggi_best')
