from abc import abstractmethod
import copy
import random
import time
from collections import deque
from ..base import AbstractAlgorithm

class RandomSearch(AbstractAlgorithm):
    def __init__(self, software):
        super().__init__(software)
        self.stats.update({'steps': 0})
        self.config['adaptive'] = False
        self.config['dist_max'] = 10

    def run(self):
        # start!
        self.stats['wallclock_start'] = time.time()
        self.do_run(self.initial)
        if not self.initial in self.fails:
            self.best = copy.deepcopy(self.initial)
            print('initial: {}'.format(self.fitness(self.best)))
        else:
            print('initial solution has failed')
            return

        # main loop
        while not self.stopping_condition():
            self.stats['steps'] += 1

            # move
            dist = 1 + int(random.random()*self.config['dist_max']-1)
            current = copy.deepcopy(self.best if self.config['adaptive'] else self.initial)
            for _ in range(dist):
                current = self.mutate(current)

            # compare
            self.do_run(current)
            if self.fit_dominates(current, self.best):
                self.best = copy.deepcopy(current)
                print('new BEST! {}'.format(self.fitness(self.best)))
            # else:
            #     print('rejected: {} > {}'.format(self.fitness(current), self.fitness(self.best)))

        # the end
        self.stats['wallclock_end'] = time.time()
        print('===== END ({:.2f}s) ====='.format(self.stats['wallclock_end'] - self.stats['wallclock_start']))

    @abstractmethod
    def mutate(self, sol):
        pass

    def stopping_condition(self):
        now = time.time()
        return now > self.stats['wallclock_start'] + 30 # default: 30 seconds

    def break_condition(self):
        return False
