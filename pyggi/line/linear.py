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
    def alter(self, software):
        software.do_delete(self.target)

class LineReplacement(TargetIngredientEdit):
    def alter(self, software):
        software.do_replace(self.target, self.ingredient)

class LineSwap(TargetIngredientEdit):
    def alter(self, software):
        software.do_swap(self.target, self.ingredient)

class LineInsertionBefore(TargetIngredientEdit):
    def alter(self, software):
        software.do_insert_before(self.target, self.ingredient)

class LineMoveBefore(TargetIngredientEdit):
    def alter(self, software):
        software.do_insert_before(self.target, self.ingredient)
        software.do_delete(self.ingredient)
