from abc import abstractmethod
from ..base import TargetEdit, TargetIngredientEdit, Software

class LinearSoftware(Software):
    @abstractmethod
    def do_delete(self, target):
        pass

    @abstractmethod
    def do_replace(self, target, ingredient):
        pass

    @abstractmethod
    def do_swap(self, target, ingredient):
        pass

    @abstractmethod
    def do_insert_before(self, target, ingredient):
        pass


class LineDeletion(TargetEdit):
    def __str__(self):
        return 'LineDeletion({})'.format(self.target)

    def alter(self, software):
        software.do_delete(self.target)

class LineReplacement(TargetIngredientEdit):
    def __str__(self):
        return 'LineReplacement({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_replace(self.target, self.ingredient)

class LineSwap(TargetIngredientEdit):
    def __str__(self):
        return 'LineSwap({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_swap(self.target, self.ingredient)

class LineInsertionBefore(TargetIngredientEdit):
    def __str__(self):
        return 'LineInsertionBefore({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_insert_before(self.target, self.ingredient)

class LineMoveBefore(TargetIngredientEdit):
    def __str__(self):
        return 'LineMoveBefore({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_insert_before(self.target, self.ingredient)
        software.do_delete(self.ingredient)
