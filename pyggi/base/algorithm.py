from abc import ABC, abstractmethod
import copy

class AbstractAlgorithm(ABC):
    def __init__(self, software):
        self.software = software
        self.config = dict()
        self.best = None
        self.fails = set()
        self.runs = dict()
        self.tests = dict()
        self.stats = {'tests': 0, 'runs': 0}

    def setup(self):
        pass

    def fitness(self, sol):
        if sol in self.runs:
            return self.runs[sol]
        return None

    def dominates(self, before, after):
        # print('dominates?', before, after)
        return before and ((not after) or (before < after))

    def fit_dominates(self, sol_before, sol_after):
        return self.dominates(self.fitness(sol_before), self.fitness(sol_after))

    def do_run(self, sol, detail=1):
        if sol in self.runs or sol in self.fails:
            return
        self.stats['tests'] += 1
        mutant = copy.deepcopy(self.software)
        mutant.apply(sol)
        mutant.ready()
        if not mutant.test():
            self.fails.add(sol)
            return
        run = mutant.run()
        if run:
            self.runs[sol] = run
        else:
            self.fails.add(sol)
        self.stats['runs'] += 1
