from abc import abstractmethod
from copy import deepcopy
from random import random
from time import time
from collections import deque
from ..abstract import AbstractAlgorithm

class RandomSearch(AbstractAlgorithm):
    def __init__(self, software):
        super().__init__(software)
        self.stats.update({'steps': 0})
        self.config['adaptive'] = False
        self.config['dist_max'] = 10

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
        while not self.stopping_condition():
            self.stats['steps'] += 1

            # move
            dist = 1 + int(random()*self.config['dist_max']-1)
            current = deepcopy(self.best if self.config['adaptive'] else initial_sol)
            for _ in range(dist):
                current = self.mutate(current)

            # compare
            self.do_run(current)
            if self.fit_dominates(current, self.best):
                self.best = deepcopy(current)
                print('new BEST! {}'.format(self.fitness(self.best)))
            # else:
            #     print('rejected: {} > {}'.format(self.fitness(current), self.fitness(self.best)))

        # the end
        self.stats['wallclock_end'] = time()
        print('===== END ({:.2f}s) ====='.format(self.stats['wallclock_end'] - self.stats['wallclock_start']))

    @abstractmethod
    def mutate(self, sol):
        pass

    def stopping_condition(self):
        now = time()
        return now > self.stats['wallclock_start'] + 30 # default: 30 seconds

    def break_condition(self):
        return False
