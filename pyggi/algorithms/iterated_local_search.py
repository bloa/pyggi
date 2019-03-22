from abc import abstractmethod
import copy
import random
import time
from ..base import AbstractAlgorithm

class IteratedLocalSearch(AbstractAlgorithm):
    def setup(self):
        self.stats['iteration'] = 0
        self.stats['steps'] = 0
        self.stats['cons_worse'] = 0
        self.stats['cons_tabu'] = 0
        self.config['perturb_length'] = 3

    def run(self):
        # start!
        self.stats['wallclock_start'] = time.time()
        self.do_run(self.initial)
        if not self.initial in self.fails:
            self.best = copy.deepcopy(self.initial)
            if self.verbose > 0:
                print('initial:', self.fitness(self.best))
        else:
            if self.verbose > 0:
                print('initial solution has failed')
            return

        # main loop
        current = copy.deepcopy(self.best)
        while not self.stopping_condition():
            self.stats['iteration'] += 1
            self.stats['steps'] += 1
            if self.verbose > 0:
                print()
                print('===== Iteration {} ====='.format(self.stats['iteration']))
            # restart or perturb
            if self.restart_condition():
                if self.verbose > 0:
                    print('*** restart ***')
                current = copy.deepcopy(self.initial)
            elif self.perturb_condition():
                if self.verbose > 0:
                    print('*** perturb ***')
                tries = 3
                while tries > 0:
                    tries -= 1
                    tmp = self.perturb(copy.deepcopy(current))
                    self.do_run(tmp)
                    if not tmp in self.fails:
                        current = tmp
                        break
                else: # restart
                    if self.verbose > 0:
                        print('... perturb failed')
                        print('*** restart ***')
                    current = copy.deepcopy(self.initial)
            if self.verbose > 0:
                print('best:', self.fitness(self.best))
                print('current:', self.fitness(current))

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
                    if self.verbose > 1:
                        print('trying:', neighbour)
                    self.do_run(neighbour)
                    if self.accept(current, neighbour):
                        if self.verbose > 0:
                            print('current:', self.fitness(neighbour))
                        current = neighbour
                        self.stats['cons_worse'] = 0
                        if self.fit_dominates(current, self.best):
                            if self.verbose > 0:
                                print('new BEST!', self.fitness(current))
                            self.best = copy.deepcopy(current)

                        break
                    else:
                        self.stats['cons_worse'] += 1
                        if self.verbose > 1:
                            print('rejected: {} (best: {})'.format(self.fitness(neighbour), self.fitness(current)))
                if self.break_condition() or self.stats['cons_worse'] > 0:
                    break

        # the end
        self.stats['wallclock_end'] = time.time()
        if self.verbose > 0:
            print('===== END ({:.2f}s) ====='.format(self.stats['wallclock_end'] - self.stats['wallclock_start']))

    @abstractmethod
    def neighbourhood(self, sol):
        pass

    def perturb(self, sol):
        sol = copy.deepcopy(sol)
        for _ in range(self.config['perturb_length']):
            sol = next(self.neighbourhood(sol))
        return sol

    def accept(self, before, after):
        return not self.fit_dominates(before, after)

    def stopping_condition(self):
        now = time.time()
        return now > self.stats['wallclock_start'] + 30 # default: 30 seconds

    def restart_condition(self):
        return random.random() < 0.01

    def perturb_condition(self):
        return self.stats['iteration'] > 1

    def stuck_condition(self):
        return self.stats['cons_worse'] > 99

    def break_condition(self):
        return self.stats['cons_tabu'] > 99
