import astor
import os
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
        target_path = self.modification_points[target_file][target_point]
        astor_helper.replace(
            (self.contents[target_file], target_path),
            None)

    def do_replace_tree(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        target_path = self.modification_points[target_file][target_point]
        ingredient_path = self.modification_points[ingredient_file][ingredient_point]
        astor_helper.replace(
            (self.contents[target_file], target_path),
            (self.contents[ingredient_file], ingredient_path))

    def do_swap_tree(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        target_path = self.modification_points[target_file][target_point]
        ingredient_path = self.modification_points[ingredient_file][ingredient_point]
        astor_helper.swap(
            (self.contents[target_file], target_path),
            (self.contents[ingredient_file], ingredient_path))

    def do_insert_tree_before(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        target_path = self.modification_points[target_file][target_point]
        ingredient_path = self.modification_points[ingredient_file][ingredient_point]
        success = astor_helper.insert_before(
            (self.contents[target_file], target_path),
            (self.contents[ingredient_file], ingredient_path))
        if success:
            depth = len(target_path)
            parent = target_path[:depth-1]
            index = target_path[depth-1][1]
            for pos in self.modification_points[target_file]:
                if parent == pos[:depth-1] and len(pos) >= depth and index <= pos[depth-1][1]:
                    a, i = pos[depth-1]
                    pos[depth-1] = (a, i + 1)
