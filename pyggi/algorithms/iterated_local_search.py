from abc import abstractmethod
from copy import deepcopy
from random import random
from time import time
from ..base import AbstractAlgorithm

class IteratedLocalSearch(AbstractAlgorithm):
    def __init__(self, software):
        super().__init__(software)
        self.stats.update({'iteration': 0, 'steps': 0, 'cons_worse': 0, 'cons_tabu': 0})
        self.config['perturb_length'] = 3

    def run(self, initial_sol):
        # start!
        self.stats['wallclock_start'] = time()
        self.do_run(initial_sol)
        if not initial_sol in self.fails:
            self.best = initial_sol
            print('initial: {}'.format(self.fitness(self.best)))
        else:
            print('initial solution has failed')
            return

        # main loop
        current = deepcopy(self.best)
        while not self.stopping_condition():
            self.stats['iteration'] += 1
            print()
            print('===== Iteration {} ====='.format(self.stats['iteration']))
            # restart or perturb
            if self.restart_condition():
                print('*** restart ***')
                current = deepcopy(initial_sol)
            elif self.perturb_condition():
                print('*** perturb ***')
                while True:
                    tmp = self.perturb(deepcopy(current))
                    self.do_run(tmp)
                    if not tmp in self.fails:
                        current = tmp
                        break
            print('best: {}'.format(self.fitness(self.best)))
            print('current: {}'.format(self.fitness(current)))

            # descent
            tabu = set()
            tabu.add(current)
            self.stats['cons_worse'] = 0
            while not self.stuck_condition() and not self.stopping_condition():
                # neighbourhood search
                self.stats['cons_tabu'] = 0
                for neighbour in self.neighbourhood(current):
                    if self.break_condition() or self.stuck_condition() or self.stopping_condition():
                        break
                    if neighbour in tabu:
                        self.stats['cons_tabu'] += 1
                        continue
                    self.stats['cons_tabu'] = 0
                    tabu.add(neighbour)
                    self.stats['steps'] += 1
                    self.do_run(neighbour)
                    if self.accept(current, neighbour):
                        print('current {}'.format(self.fitness(neighbour)))
                        current = neighbour
                        self.stats['cons_worse'] = 0
                        break
                    else:
                        self.stats['cons_worse'] += 1
                        # print('rejected: {} > {}'.format(self.fitness(neighbour), self.fitness(current)))
                if self.break_condition() or self.stats['cons_worse'] > 0:
                    break
            if self.accept(self.best, current):
                print('new BEST! {}'.format(self.fitness(current)))
                self.best = deepcopy(current)

        # the end
        self.stats['wallclock_end'] = time()
        print('===== END ({:.2f}s) ====='.format(self.stats['wallclock_end'] - self.stats['wallclock_start']))

    @abstractmethod
    def neighbourhood(self, sol):
        pass

    def perturb(self, sol):
        sol = deepcopy(sol)
        for _ in range(self.config['perturb_length']):
            sol = next(self.neighbourhood(sol))
        return sol

    def accept(self, before, after):
        return not self.fit_dominates(before, after)

    def stopping_condition(self):
        now = time()
        return now > self.stats['wallclock_start'] + 30 # default: 30 seconds

    def restart_condition(self):
        return random() < 0.01

    def perturb_condition(self):
        return self.stats['iteration'] > 1

    def stuck_condition(self):
        return self.stats['cons_worse'] > 99

    def break_condition(self):
        return self.stats['cons_tabu'] > 99
