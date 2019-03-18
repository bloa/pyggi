from abc import abstractmethod
from ..base import AbstractEdit, Software

class TreeSoftware(Software):
    @abstractmethod
    def do_delete_tree(self, target):
        pass

    @abstractmethod
    def do_copy_tree(self, target, ingredient):
        pass

    @abstractmethod
    def do_insert_tree_before(self, target, ingredient):
        pass
