import copy
import inspect
import importlib
import json
import os
import random
import signal
import sys
import time
from pyggi.algorithms import IteratedLocalSearch
from pyggi.line import LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore
from pyggi.line import LineProgram

PYTHON_DIR = '../sample/quixbugs/python_programs'
JSON_DIR = '../sample/quixbugs/json_testcases'

class MyProgram(LineProgram):
    def test(self):
        (algo, _) = os.path.splitext(self.config['target_files'][0])
        # todo: change "/" to "." with re
        path = '{}.{}'.format(os.path.normpath(self.path), algo)
        try:
            self.fx = None
            if path in sys.modules:
                del sys.modules[path]
            module = importlib.__import__(path)
            # importlib.reload(module) # ???
            self.fx = getattr(getattr(module, algo), algo)
            # print(inspect.getsource(self.fx))
        except:
            return False
        return True

    def run(self):
        n = len(self.config['test_cases'])
        for test_case in self.config['test_cases']:
            test_input, test_output = copy.deepcopy(test_case)
            if not isinstance(test_input, list):
                test_input = [test_input]
            try:
                sys.stdout = None
                sys.stderr = None
                signal.signal(signal.SIGALRM, lambda _,__: 1/0)
                signal.setitimer(signal.ITIMER_REAL, 0.01)
                if self.fx(*test_input) == test_output:
                    n -= 1
            except:
                pass
            finally:
                signal.alarm(0)
                sys.stdout = sys.__stderr__
                sys.stderr = sys.__stderr__
        return n

EDITS = [LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore]

class MyAlgo(IteratedLocalSearch):
    def stopping_condition(self):
        now = time.time()
        return self.fitness(self.best) == 0 or now > self.stats['wallclock_start'] + 1

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
    json_files = os.listdir(JSON_DIR)
    success = list()
    for filename in json_files:
        (name, _) = os.path.splitext(filename)
        print('===== {} ====='.format(name))
        content = open('../sample/quixbugs/json_testcases/{}.json'.format(name), 'r')
        acc = list()
        for line in content:
            acc.append(json.loads(line))

        config = {
            'path': PYTHON_DIR,
            'target_files': ['{}.py'.format(name)],
            'test_cases': acc,
        }

        software = MyProgram(config)
        algo = MyAlgo(software)
        algo.run()

        print()
        print('===== Finish =====')
        print(algo.stats)
        print('best fitness:', algo.fitness(algo.best))
        print(algo.best)
        print()
        if algo.fit_dominates(algo.best, algo.initial):
            success.append(filename)
            print('Success(es?!):', success)
            soft = copy.deepcopy(software)
            algo.best.alter(soft)
            print(soft)
    print()
    print('Success(es?!):', success)
