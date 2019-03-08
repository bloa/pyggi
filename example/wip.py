from pyggi.algorithms import IteratedLocalSearch, GeneticProgramming, TabuSearch
# from pyggi.gi.xml import Program
from pyggi.patch.abstract import AbstractSoftware
from pyggi.patch.abstract import AbstractAtomicOperator
from pyggi.patch import Patch
from random import random
from copy import deepcopy

class FakeEdit(AbstractAtomicOperator):
    def __init__(self):
        self.fake = int(random()*100)
        pass
    def __str__(self):
        return 'FE({})'.format(self.fake)
    def apply(self):
        pass
    def create(self):
        pass
    def is_valid_for(self, _):
        return True
    def modification_point(self):
        pass

class MySoftware(AbstractSoftware):
    def initial(self):
        return Patch(self)

    def test(self, patch):
        return random() < 1/(1+len(patch))

    def run(self, patch):
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
            sol.edit_list.pop(int(random()*len(sol)))
        else:
            sol.edit_list.append(FakeEdit())
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
            sol.remove(int(random()*len(sol)))
        else:
            sol.add(FakeEdit())
        return sol

    def crossover(self, sol1, sol2):
        c = deepcopy(sol1)
        for edit in sol2.edit_list:
            c.add(edit)
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
            sol.remove(int(random()*len(sol)))
        else:
            sol.add(FakeEdit())
        return sol


software = MySoftware()
algo = MyAlgo3(software)

try:
    algo.run(software.initial())
finally:
    print()
    print('===== Final =====')
    print(algo.stats)
    print('best fitness:', algo.fitness(algo.best))
    print(algo.best)
