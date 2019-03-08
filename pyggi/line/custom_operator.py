from ..abstract import AbstractCustomOperator
from . import Program as LineProgram


class LineDeletion(AbstractCustomOperator):
    """
    LineDeletion: Delete x

    It replaces the code line with an empty line.
    """
    def __str__(self):
        return "LineDeletion({})".format(self.x)

    def is_valid_for(self, program):
        return isinstance(program, LineProgram)

    @property
    def x(self):
        """
        Delete **x**

        :return: The file path and the index of target line to be deleted.
        :rtype: tuple(str, int)
        """
        return self.args[0]

    @property
    def length_of_args(self):
        """
        :return: ``1``
        :rtype: int
        """
        return 1

    @property
    def atomic_operators(self):
        """
        :return: ``[LineReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        from .atomic_operator import LineReplacement
        return [LineReplacement(self.x, None)]

    @classmethod
    def create(cls, program, line_file=None, method='random'):
        """
        :param program: The program instance to which the random custom operator will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line is the target line to delete.
          If line_file is specified, the target line will be chosen within the file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The LineDeletion instance with the randomly-selected line index.
        :rtype: :py:class:`.custom_operator.LineDeletion`
        """
        import random
        line_file = line_file or random.choice(program.target_files)
        line = (
            line_file,
            program.select_modification_point(line_file, method)
        )
        return cls(line)

class LineMoving(AbstractCustomOperator):
    """
    LineMoving: Move x [before|after] y
    """
    def __str__(self):
        return "LineMoving({}, {}, '{}')".format(self.y, self.x, self.direction)

    def is_valid_for(self, program):
        return isinstance(program, LineProgram)

    @property
    def x(self):
        """
        Move **x** [before|after] y

        :return: The file path and the index of target line to be moved.
        :rtype: tuple(str, int)
        """
        return self.args[1]

    @property
    def y(self):
        """
        Move x [before|after] **y**

        :return: The file path and the index of the point to which line x is inserted.
        :rtype: tuple(str, int)
        """
        return self.args[0]

    @property
    def direction(self):
        """
        Move x **[before|after]** y

        :return: **'before'** or **'after'**
        :rtype: str
        """
        return self.args[2]

    @property
    def length_of_args(self):
        """
        :return: ``3``
        :rtype: int
        """
        return 3

    @property
    def atomic_operators(self):
        """
        :return: ``[LineInsertion(self.y, self.x, self.direction), LineReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        from .atomic_operator import LineInsertion, LineReplacement
        return [LineInsertion(self.y, self.x, self.direction), LineReplacement(self.x, None)]

    @classmethod
    def create(cls, program, line_file=None, ingr_file=None, direction='before', method='random'):
        """
        :param program: The program instance to which the created custom operator will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: Line means the modification point of the edit. If line_file is specified, the line will be chosen within the file.
        :param str ingr_file: Ingredient is the line to be moved.
          If ingr_file is specified, the ingredient line will be chosen within the file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The LineMoving instance with the randomly-selected line & ingr.
        :rtype: :py:class:`.custom_operator.LineMoving`
        """
        import random
        line_file = line_file or random.choice(program.target_files)
        ingr_file = ingr_file or random.choice(program.target_files)
        line = (
            line_file,
            program.select_modification_point(line_file, method)
        )
        ingredient = (
            ingr_file,
            program.select_modification_point(ingr_file, 'random')
        )
        return cls(ingredient, line, direction)
