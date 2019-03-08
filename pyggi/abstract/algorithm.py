"""

This module contains meta-heuristic search algorithms.

"""

from abc import ABC, abstractmethod

class AbstractAlgorithm(ABC):
    """
    Algorithm (Abstract Class)

    All children classes need to override

    * :py:meth:`get_fitness`
    """

    def __init__(self, program):
        """
        :param program: The Program instance to optimize.
        :type program: :py:class:`.Program`
        """
        self.program = program

    @abstractmethod
    def get_fitness(self, patch):
        """
        Define the fitness value of the patch

        If you want to use original one(elapsed_time),
        simply call ``super()``.

        :param patch: The patch instacne
        :type patch: :py:class:`.Patch`
        :return: The fitness value
        """
        return patch.test_result.elapsed_time
