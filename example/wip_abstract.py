import copy
import random
from pyggi.base import AbstractSoftware, AbstractEdit
from pyggi.algorithms import IteratedLocalSearch, GeneticProgramming, TabuSearch

class FakeEdit(AbstractEdit):
    def __init__(self):
        self.fake = int(random.random()*100)
    def __eq__(self, other):
        self.fake == other.fake
    def __str__(self):
        return 'FE({})'.format(self.fake)
    def alter(self, software):
        pass

class MySoftware(AbstractSoftware):
    def test(self):
        return random.random() < 1/(1+len(self.patch))

    def run(self):
        return int(10000000*random.random())

class MyAlgo(IteratedLocalSearch):
    def stopping_condition(self):
        return self.stats['iteration'] == 10

    def neighbourhood(self, sol):
        for _ in range(100): # neighbourhood size
            c = copy.deepcopy(sol)
            yield self.mutate(c)

    def mutate(self, sol):
        if len(sol) > 1 and random.random() > 0.5:
            sol.edits.pop(int(random.random()*len(sol)))
        else:
            sol.edits.append(FakeEdit())
        return sol

if __name__ == "__main__":
    software = MySoftware()
    algo = MyAlgo(software)

    try:
        algo.run()
    finally:
        print()
        print('===== Final =====')
        print(algo.stats)
        print('best fitness:', algo.fitness(algo.best))
        print(algo.best)
