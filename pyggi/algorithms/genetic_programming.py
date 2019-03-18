from abc import abstractmethod
from copy import deepcopy
from random import random, sample, shuffle
from time import time
from ..base import AbstractAlgorithm

class GeneticProgramming(AbstractAlgorithm):
    def __init__(self, software):
        super().__init__(software)
        self.stats.update({'generation': 0})
        self.config['pop_size'] = 10

    def run(self, initial_sol):
        # setup
        self.setup()

        # start!
        self.stats['wallclock_start'] = time()
        self.do_run(initial_sol)
        if not initial_sol in self.fails:
            self.best = initial_sol
            print('initial: {}'.format(self.fitness(self.best)))
        else:
            print('initial solution has failed')
            return

        # initial pop
        pop = list()
        while len(pop) < self.config['pop_size']:
            sol = self.mutate(deepcopy(initial_sol))
            pop.append(sol)

        print()
        print('===== Generation {} ====='.format(self.stats['generation']))
        # compute fitness
        tmp = None
        for sol in pop:
            self.do_run(sol)
            print(self.fitness(sol))
            if self.fit_dominates(sol, tmp):
                tmp = sol
        if self.fit_dominates(tmp, self.best):
            print('new BEST! {}'.format(self.fitness(tmp)))
            self.best = deepcopy(tmp)

        # main loop
        while not self.stopping_condition():
            self.stats['generation'] += 1
            print()
            print('===== Generation {} ====='.format(self.stats['generation']))
            offsprings = list()
            parents = self.select(pop)
            # crossover
            for parent in deepcopy(parents):
                sol = self.crossover(parent, sample(pop, 1)[0])
                offsprings.append(sol)
            # mutation
            for parent in deepcopy(parents):
                sol = self.mutate(parent)
                offsprings.append(sol)
            # regrow
            while len(offsprings) < self.config['pop_size']:
                sol = self.mutate(deepcopy(initial_sol))
                offsprings.append(sol)
            # replace
            pop = offsprings
            # compute fitness
            tmp = None
            for sol in pop:
                self.do_run(sol)
                print(self.fitness(sol))
                if self.fit_dominates(sol, tmp):
                    tmp = sol
            if self.fit_dominates(tmp, self.best):
                print('new BEST! {}'.format(self.fitness(tmp)))
                self.best = deepcopy(tmp)

        # the end
        self.stats['wallclock_end'] = time()
        print('===== END ({:.2f}s) ====='.format(self.stats['wallclock_end'] - self.stats['wallclock_start']))

    @abstractmethod
    def select(self, pop):
        pass

    @abstractmethod
    def crossover(self, sol1, sol2):
        pass

    @abstractmethod
    def mutate(self, sol):
        pass

    def stopping_condition(self):
        False

    def restart_condition(self):
        return random() < 0.01

    def perturb_condition(self):
        return self.stats['generation'] > 1

    def stuck_condition(self):
        return self.stats['cons_worse'] > 9

    def break_condition(self):
        return self.stats['cons_tabu'] > 9
