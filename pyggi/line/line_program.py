import os
import random
from . import LinearSoftware

class LineProgram(LinearSoftware):
    def __str__(self):
        code = []
        for k in sorted(self.contents.keys()):
            for idx, line in enumerate(self.contents[k]):
                try:
                    mpidx = '({})'.format(self.modification_points[k].index(idx))
                except ValueError:
                    mpidx = '   '
                code.append("{}\t: {} {}\t: {}".format(k, idx, mpidx, line))
        return '\n'.join(code)

    def parse(self, path):
        self.contents = {}
        self.modification_points = {}
        for target in self.config['target_files']:
            with open(os.path.join(path, target), 'r') as target_file:
                self.contents[target] = list(map(str.rstrip, target_file.readlines()))
                self.modification_points[target] = list(range(len(self.contents[target])))

    def synthetise(self, target):
        return '{}\n'.format('\n'.join(self.contents[target]))

    def do_delete(self, target):
        target_file, target_point = target
        self.contents[target_file][self.modification_points[target_file][target_point]] = ''

    def do_replace(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        # tmp = self.contents[ingredient_file][ingredient_point] # why?
        tmp = self.contents[ingredient_file][self.modification_points[ingredient_file][ingredient_point]]
        self.contents[target_file][self.modification_points[target_file][target_point]] = tmp

    def do_swap(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        tmp1 = self.contents[target_file][self.modification_points[target_file][target_point]]
        tmp2 = self.contents[ingredient_file][self.modification_points[ingredient_file][ingredient_point]]
        self.contents[target_file][self.modification_points[target_file][target_point]] = tmp2
        self.contents[ingredient_file][self.modification_points[ingredient_file][ingredient_point]] = tmp1

    def do_insert_before(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        # tmp = self.contents[ingredient_file][ingredient_point] # why?
        tmp = self.contents[ingredient_file][self.modification_points[ingredient_file][ingredient_point]]
        self.contents[target_file].insert(self.modification_points[target_file][target_point], tmp)
        for i in range(target_point, len(self.modification_points[target_file])):
            self.modification_points[target_file][i] += 1
