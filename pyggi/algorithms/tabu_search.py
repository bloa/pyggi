from abc import abstractmethod
import copy
import time
import collections
from ..base import AbstractAlgorithm

class TabuSearch(AbstractAlgorithm):
    def __init__(self, software):
        super().__init__(software)
        self.stats.update({'iteration': 0, 'steps': 0})
        self.config['tabu_length'] = 10
        self.tabu = collections.deque()

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
        current = copy.deepcopy(self.best)
        self.make_tabu(current)
        self.stats['iteration'] += 1
        print()
        print('===== Iteration {} ====='.format(self.stats['iteration']))
        while not self.stopping_condition():
            # neighbourhood search
            local_best = None
            for neighbour in self.neighbourhood(current):
                if self.stopping_condition():
                    break
                if self.is_tabu(neighbour):
                    continue
                self.do_run(neighbour)
                if self.fit_dominates(neighbour, local_best):
                    local_best = neighbour
                # else:
                #     print('rejected: {} > {}'.format(self.fitness(neighbour), self.fitness(local_best)))
            if local_best and self.fitness(local_best):
                self.stats['steps'] += 1
                current = local_best
                print('current {}'.format(self.fitness(current)))
                self.make_tabu(current)
                if self.fit_dominates(current, self.best):
                    self.best = copy.deepcopy(current)
                    print('new BEST! {}'.format(self.fitness(self.best)))
            else: # restart
                self.stats['iteration'] += 1
                print()
                print('===== Iteration {} ====='.format(self.stats['iteration']))
                print('*** restart ***')
                self.stats['steps'] += 1
                current = copy.deepcopy(self.initial)
                self.clear_tabu()
                self.make_tabu(current)
                print('best: {}'.format(self.fitness(self.best)))
                print('current: {}'.format(self.fitness(current)))

        # the end
        self.stats['wallclock_end'] = time.time()
        print('===== END ({:.2f}s) ====='.format(self.stats['wallclock_end'] - self.stats['wallclock_start']))

    @abstractmethod
    def neighbourhood(self, sol):
        pass

    def is_tabu(self, sol):
        return sol in self.tabu

    def make_tabu(self, sol):
        self.tabu.append(sol)
        while len(self.tabu) >= self.config['tabu_length']:
            self.tabu.popleft()

    def clear_tabu(self, sol):
        self.tabu.clear()

    def stopping_condition(self):
        now = time.time()
        return now > self.stats['wallclock_start'] + 30 # default: 30 seconds

    def break_condition(self):
        return False
