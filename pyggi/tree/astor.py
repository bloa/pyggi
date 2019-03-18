import astor
import os
import random
from . import TreeSoftware
from . import astor_helper

class AstorProgram(TreeSoftware):
    def parse(self, path):
        self.contents = {}
        self.modification_points = {}
        for target in self.config['target_files']:
            _, extension = os.path.splitext(target)
            assert(extension ==  '.py')
            self.contents[target] = astor.parse_file(os.path.join(path, target))
            self.modification_points[target] = astor_helper.get_modification_points(self.contents[target])

    def synthetise(self, target):
        return astor.to_source(self.contents[target])

    def do_delete_tree(self, target):
        target_file, target_point = target
        return astor_helper.replace(
            (self.contents[target_file], self.modification_points[target_file][target_point]),
            None)

    def do_replace_tree(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        return astor_helper.replace(
            (self.contents[target_file], self.modification_points[target_file][target_point]),
            (self.contents[ingredient_file], self.modification_points[ingredient_file][ingredient_point]))
