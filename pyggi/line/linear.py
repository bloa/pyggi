from abc import abstractmethod
from ..base import AbstractEdit, Software

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


class LineDeletion(AbstractEdit):
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return 'LineDeletion({})'.format(self.target)

    def alter(self, software):
        software.do_delete(self.target)

    @classmethod
    def create(cls, software):
        return cls(software.random_target())

class LineReplacement(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return 'LineReplacement({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_replace(self.target, self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_target())

class LineSwap(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return 'LineSwap({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_swap(self.target, self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_target())

class LineInsertionBefore(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return 'LineInsertionBefore({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_insert_before(self.target, self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_target())

class LineMoveBefore(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return 'LineMoveBefore({}, {})'.format(self.target, self.ingredient)

    def alter(self, software):
        software.do_insert_before(self.target, self.ingredient)
        software.do_delete(self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_target())
