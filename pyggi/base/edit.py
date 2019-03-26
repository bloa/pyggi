from abc import ABC, abstractmethod

class AbstractEdit(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def alter(self, software):
        pass


class TargetEdit(AbstractEdit):
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.target)

    @classmethod
    def create(cls, software):
        return cls(software.random_target())


class TargetIngredientEdit(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def __str__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.target, self.ingredient)

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_ingredient())

