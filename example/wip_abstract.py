from pyggi.abstract import AbstractSoftware, AbstractEdit, Patch
from pyggi.algorithms import IteratedLocalSearch, GeneticProgramming, TabuSearch
from random import random
from copy import deepcopy

class FakeEdit(AbstractEdit):
    def __init__(self):
        self.fake = int(random()*100)
    def __eq__(self, other):
        self.fake == other.fake
    def __str__(self):
        return 'FE({})'.format(self.fake)
    def alter(self, software):
        pass

class MySoftware(AbstractSoftware):
    def test(self):
        return random() < 1/(1+len(self.patch))

    def run(self):
        return int(10000000*random())

class MyAlgo(IteratedLocalSearch):
    def stopping_condition(self):
        return self.stats['iteration'] == 10

    def neighbourhood(self, sol):
        for _ in range(100): # neighbourhood size
            c = deepcopy(sol)
            yield self.mutate(c)

    def mutate(self, sol):
        if len(sol) > 1 and random() > 0.5:
            sol.edits.pop(int(random()*len(sol)))
        else:
            sol.edits.append(FakeEdit())
        return sol

if __name__ == "__main__":
    software = MySoftware()
    algo = MyAlgo(software)

    try:
        patch = Patch()
        algo.run(patch)
    finally:
        print()
        print('===== Final =====')
        print(algo.stats)
        print('best fitness:', algo.fitness(algo.best))
        print(algo.best)
