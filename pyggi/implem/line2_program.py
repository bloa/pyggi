import os
import random
from ..granularity import LinearSoftware

class Line2Program(LinearSoftware):
    def __str__(self):
        code = []
        for k in sorted(self.contents.keys()):
            for idx, a in enumerate(self.contents[k]):
                for line in a[2]:
                    code.append("{}\t: vvv\t: {}".format(k, line))
                code.append("{}\t: {}\t: {}".format(k, idx, a[1]))
        return '\n'.join(code)

    def parse(self, path):
        self.contents = {}
        self.modification_points = {}
        for target in self.config['target_files']:
            with open(os.path.join(path, target), 'r') as target_file:
                tmp = map(str.rstrip, target_file.readlines())
                self.contents[target] = list(map(lambda s: [s, s, []], tmp))
                self.modification_points[target] = list(range(len(self.contents[target])))

    def synthetise(self, target):
        tmp = [a[2]+[a[1]] for a in self.contents[target]]
        return '{}\n'.format('\n'.join(sum(tmp)))

    def write(self, path):
        for target in self.config['target_files']:
            with open(os.path.join(path, target), 'w') as target_file:
                target_file.write(self.synthetise(target))

    def do_delete(self, target):
        target_file, target_point = target
        self.contents[target_file][target_point][1] = ''

    def do_replace(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        tmp = self.contents[ingredient_file][ingredient_point]
        self.contents[target_file][target_point][1] = tmp[0]

    def do_swap(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        tmp1 = self.contents[target_file][target_point][0]
        tmp2 = self.contents[ingredient_file][ingredient_point][0]
        self.contents[target_file][target_point][1] = tmp2
        self.contents[ingredient_file][ingredient_point][1] = tmp1

    def do_insert_before(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        tmp = self.contents[ingredient_file][ingredient_point][1]
        self.contents[target_file][target_point][2].insert(0, tmp)
