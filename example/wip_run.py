import copy
import random
from pyggi.algorithms import IteratedLocalSearch
from pyggi.line import LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore
from pyggi.line import LineProgram

class MyProgram(LineProgram):
    def parse_output(self, stdout, stderr):
        try:
            return int(stdout)
        except:
            return None

EDITS = [LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore]

class MyAlgo(IteratedLocalSearch):
    def dominates(self, before, after):
        return (before is not None) and ((after is None) or (before > after))

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
        'target_files': ['foo_numbers.py'],
        'run_cmd': 'python foo_numbers.py',
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
    print(soft)
