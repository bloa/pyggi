from abc import abstractmethod
from ..base import AbstractEdit, Software

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


class TreeDeletion(AbstractEdit):
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return 'TreeDeletion({})'.format(self.target)

    def alter(self, software):
        software.do_delete_tree(self.target)

    @classmethod
    def create(cls, software):
        return cls(software.random_target())

class TreeReplacement(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return 'TreeReplacement({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_replace_tree(self.target, self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_target())

class TreeSwap(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return 'TreeSwap({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_swap_tree(self.target, self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_target())

class TreeInsertionBefore(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return 'TreeInsertionBefore({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_insert_tree_before(self.target, self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_target())

class TreeMoveBefore(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return 'TreeMoveBefore({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_insert_tree_before(self.target, self.ingredient)
        software.do_delete_tree(self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_target())
