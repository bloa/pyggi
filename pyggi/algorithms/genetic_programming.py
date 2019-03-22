from abc import abstractmethod
import copy
import random
import time
from ..base import AbstractAlgorithm

class GeneticProgramming(AbstractAlgorithm):
    def setup(self):
        super().setup()
        self.stats.update({'generation': 0})
        self.config['pop_size'] = 10

    def run(self):
        # setup
        self.setup()

        # start!
        self.stats['wallclock_start'] = time.time()
        self.do_run(self.initial)
        if not self.initial in self.fails:
            self.best = copy.deepcopy(self.initial)
            if self.verbose > 0:
                print('initial: {}'.format(self.fitness(self.best)))
        else:
            if self.verbose > 0:
                print('initial solution has failed')
            return

        # initial pop
        pop = list()
        while len(pop) < self.config['pop_size']:
            sol = self.mutate(copy.deepcopy(self.initial))
            pop.append(sol)

        if self.verbose > 0:
            print()
            print('===== Generation {} ====='.format(self.stats['generation']))
        # compute fitness
        tmp = None
        for sol in pop:
            self.do_run(sol)
            if self.verbose > 1:
                print(self.fitness(sol), sol)
            elif self.verbose > 0:
                print(self.fitness(sol))
            if self.fit_dominates(sol, tmp):
                tmp = sol
        if self.fit_dominates(tmp, self.best):
            if self.verbose > 0:
                print('new BEST!', self.fitness(tmp))
            self.best = copy.deepcopy(tmp)

        # main loop
        while not self.stopping_condition():
            self.stats['generation'] += 1
            if self.verbose > 0:
                print()
                print('===== Generation {} ====='.format(self.stats['generation']))
            offsprings = list()
            parents = self.select(pop)
            # crossover
            for parent in copy.deepcopy(parents):
                sol = self.crossover(parent, random.sample(pop, 1)[0])
                offsprings.append(sol)
            # mutation
            for parent in copy.deepcopy(parents):
                sol = self.mutate(parent)
                offsprings.append(sol)
            # regrow
            while len(offsprings) < self.config['pop_size']:
                sol = self.mutate(copy.deepcopy(self.initial))
                offsprings.append(sol)
            # replace
            pop = offsprings
            # compute fitness
            tmp = None
            for sol in pop:
                self.do_run(sol)
                if self.verbose > 1:
                    print(self.fitness(sol), sol)
                elif self.verbose > 0:
                    print(self.fitness(sol))
                if self.fit_dominates(sol, tmp):
                    tmp = sol
            if self.fit_dominates(tmp, self.best):
                if self.verbose > 0:
                    print('new BEST!', self.fitness(tmp))
                self.best = copy.deepcopy(tmp)

        # the end
        self.stats['wallclock_end'] = time.time()
        if self.verbose > 0:
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
        return random.random() < 0.01

    def perturb_condition(self):
        return self.stats['generation'] > 1

    def stuck_condition(self):
        return self.stats['cons_worse'] > 9

    def break_condition(self):
        return self.stats['cons_tabu'] > 9
