from abc import ABC, abstractmethod

class AbstractEdit(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def alter(self, software):
        pass
