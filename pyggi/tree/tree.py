from abc import abstractmethod
from ..base import AbstractEdit, Software

class TreeSoftware(Software):
    @abstractmethod
    def do_delete_tree(self, target):
        pass

    @abstractmethod
    def do_replace_tree(self, target, ingredient):
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
