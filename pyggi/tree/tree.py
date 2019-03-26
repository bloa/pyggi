from abc import abstractmethod
from ..base import TargetEdit, TargetIngredientEdit, Software

class TreeSoftware(Software):
    @abstractmethod
    def do_delete_tree(self, target):
        pass

    @abstractmethod
    def do_replace_tree(self, target, ingredient):
        pass

    @abstractmethod
    def do_swap_tree(self, target, ingredient):
        pass

    @abstractmethod
    def do_insert_tree_before(self, target, ingredient):
        pass


class TreeDeletion(TargetEdit):
    def __str__(self):
        return 'TreeDeletion({})'.format(self.target)

    def alter(self, software):
        software.do_delete_tree(self.target)

class TreeReplacement(TargetIngredientEdit):
    def __str__(self):
        return 'TreeReplacement({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_replace_tree(self.target, self.ingredient)

class TreeSwap(TargetIngredientEdit):
    def __str__(self):
        return 'TreeSwap({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_swap_tree(self.target, self.ingredient)

class TreeInsertionBefore(TargetIngredientEdit):
    def __str__(self):
        return 'TreeInsertionBefore({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_insert_tree_before(self.target, self.ingredient)

class TreeMoveBefore(TargetIngredientEdit):
    def __str__(self):
        return 'TreeMoveBefore({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_insert_tree_before(self.target, self.ingredient)
        software.do_delete_tree(self.ingredient)
