"""

This module contains AbstractCustomOperator class which is an abstact base class,
and several classes inherit the AbstractCustomOperator class.
The classes are provided as examples of custom edit operator.

"""
from abc import ABC, abstractmethod
from . import AbstractAtomicOperator


class AbstractCustomOperator(ABC):
    """
    AbstractCustomOperator is an abstact class which is designed to be used
    as a basic structure of custom edit operators.

    Every class that inherits AbstractCustomOperator class must override the
    methods marked with ``@abstractmethod`` to create instances.

    * :py:meth:`__str__`
    * :py:meth:`length_of_args`
    * :py:meth:`atomic_operators`
    """
    def __init__(self, *args):
        if len(args) != self.length_of_args:
            raise Exception("{} takes {} positional argument but {} were given.".format(
                self.__class__.__name__, self.length_of_args, len(args)))
        self.args = args
        assert isinstance(self.atomic_operators, list)
        assert all(isinstance(op, AbstractAtomicOperator) for op in self.atomic_operators)

    def __eq__(self, other):
        return self.atomic_operators == other.atomic_operators

    @property
    def detail(self) -> str:
        """
        :return: The detail of this custom edit
        :rtype: str

        .. note::
            If the edit is ``LineMoving(('Triangle.java', 10), ('Triangle.java', 4))``

            returns::

                1) Insert ('Triangle.java', 4) before ('Triangle.java', 10)
                2) Replace ('Triangle.java', 4) with None
        """
        return "\n".join(
            list(
                map(lambda x: "{}) {}".format(x[0] + 1, x[1]),
                    enumerate(self.atomic_operators))))

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def is_valid_for(self, program):
        """
        :param program: The program instance to which this edit will be applied
        :type program: :py:class:`.Program`
        :return: Whether the edit is able to be applied to the program
        :rtype: bool
        """
        pass

    @property
    @abstractmethod
    def length_of_args(self):
        """
        :return: The length of args the edit operator should take
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def atomic_operators(self):
        """
        :return: The list of instances of AbstractAtomicOperator.
        :rtype: list(:py:class:`.atomic_operator.AbstractAtomicOperator`)
        """
        pass
