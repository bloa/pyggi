from pyggi.base import Patch
from pyggi.algorithms import IteratedLocalSearch
from pyggi.line import LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore
from pyggi.line import LineProgram
from random import random, choice
from copy import deepcopy

class MyProgram(LineProgram):
    def parse_output(self, stdout, stderr):
        try:
            return int(stdout)
        except:
            return None

# class MyProgram2(LineProgram):
#     def run(self):
#         start = time.time()
#         if LineProgram.run():
#             return time.time() - start
#         return None

EDITS = [LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore]

class MyAlgo(IteratedLocalSearch):
    def dominates(self, before, after):
        return before and ((not after) or (before > after))

    def stopping_condition(self):
        return self.stats['steps'] >= 30

    def neighbourhood(self, sol):
        for _ in range(100): # neighbourhood size
            c = deepcopy(sol)
            yield self.mutate(c)

    def mutate(self, sol):
        if len(sol) > 1 and random() > 0.5:
            sol.edits.pop(int(random()*len(sol)))
        else:
            sol.edits.append(choice(EDITS).create(self.software))
        return sol

if __name__ == "__main__":
    config = {
        'path': '.',
        'target_files': ['foo_numbers.py'],
        'run_cmd': 'python foo_numbers.py',
    }

    software = MyProgram(config)
    patch = Patch()

    algo = MyAlgo(software)
    algo.run(patch)

    print()
    print('===== Finish =====')
    print('best fitness:', algo.fitness(algo.best))
    print(algo.best)
    print()
    soft = deepcopy(software)
    algo.best.alter(soft)
    print(soft)
