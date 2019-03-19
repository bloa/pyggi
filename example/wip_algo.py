import copy
import random
from pyggi.base import AbstractSoftware, AbstractEdit
from pyggi.algorithms import RandomSearch, IteratedLocalSearch, GeneticProgramming, TabuSearch

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
        return self.stats['iteration'] == 3

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

class MyAlgo2(GeneticProgramming):
    def stopping_condition(self):
        return self.stats['generation'] == 3

    def select(self, pop):
        tmp = {sol for sol in pop if self.fitness(sol)}
        tmp = sorted(tmp, key=self.fitness)[:int(len(pop)/2)]
        return tmp

    def mutate(self, sol):
        if len(sol) > 1 and random.random() > 0.5:
            sol.edits.pop(int(random.random()*len(sol)))
        else:
            sol.edits.append(FakeEdit())
        return sol

    def crossover(self, sol1, sol2):
        c = copy.deepcopy(sol1)
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
                c = self.mutate(copy.deepcopy(sol))
                if c not in tabu:
                    tabu.add(c)
                    break
            else:
                return
            yield c

    def mutate(self, sol):
        if len(sol) > 1 and random.random() > 0.5:
            sol.edits.pop(int(random.random()*len(sol)))
        else:
            sol.edits.append(FakeEdit())
        return sol

class MyAlgo4(RandomSearch):
    def stopping_condition(self):
        return self.stats['steps'] >= 30

    def mutate(self, sol):
        if len(sol) > 1 and random.random() > 0.5:
            sol.edits.pop(int(random.random()*len(sol)))
        else:
            sol.edits.append(FakeEdit())
        return sol


if __name__ == "__main__":
    software = MySoftware()
    algos = [
        MyAlgo(software),
        MyAlgo2(software),
        MyAlgo3(software),
        MyAlgo4(software),
    ]

    for algo in algos:
        print('===== Start =====')
        random.seed(0)
        try:
            algo.run()
        finally:
            print()
            print('===== Finish =====')
            print(algo.stats)
            print('best fitness:', algo.fitness(algo.best))
            print(algo.best)
            print()
