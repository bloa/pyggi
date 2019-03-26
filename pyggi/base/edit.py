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

    @classmethod
    def create(cls, software):
        return cls(software.random_target())


class TargetIngredientEdit(AbstractEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    @classmethod
    def create(cls, software):
        return cls(software.random_target(), software.random_ingredient())

