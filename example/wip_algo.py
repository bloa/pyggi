from pyggi.abstract import AbstractSoftware, AbstractEdit, Patch
from pyggi.algorithms import IteratedLocalSearch, GeneticProgramming, TabuSearch
from random import random, seed
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
        return self.stats['iteration'] == 3

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

class MyAlgo2(GeneticProgramming):
    def stopping_condition(self):
        return self.stats['generation'] == 3

    def select(self, pop):
        tmp = {sol for sol in pop if self.fitness(sol)}
        tmp = sorted(tmp, key=self.fitness)[:int(len(pop)/2)]
        return tmp

    def mutate(self, sol):
        if len(sol) > 1 and random() > 0.5:
            sol.edits.pop(int(random()*len(sol)))
        else:
            sol.edits.append(FakeEdit())
        return sol

    def crossover(self, sol1, sol2):
        c = deepcopy(sol1)
        for edit in sol2.edits:
            c.edits.append(edit)
        return c

class MyAlgo3(TabuSearch):
    def stopping_condition(self):
        return self.stats['steps'] >= 30

    def neighbourhood(self, sol):
        tabu = set() # do we really care?
        for _ in range(100): # neighbourhood size
            c = None
            for _ in range(10): # allowed tries
                c = self.mutate(deepcopy(sol))
                if c not in tabu:
                    tabu.add(c)
                    break
            else:
                return
            yield c

    def mutate(self, sol):
        if len(sol) > 1 and random() > 0.5:
            sol.edits.pop(int(random()*len(sol)))
        else:
            sol.edits.append(FakeEdit())
        return sol


if __name__ == "__main__":
    software = MySoftware()
    algos = [
        MyAlgo(software),
        MyAlgo2(software),
        MyAlgo3(software),
    ]

    for algo in algos:
        print('===== Start =====')
        seed(0)
        try:
            patch = Patch()
            algo.run(patch)
        finally:
            print()
            print('===== Finish =====')
            print(algo.stats)
            print('best fitness:', algo.fitness(algo.best))
            print(algo.best)
            print()
