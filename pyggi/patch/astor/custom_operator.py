from ..abstract import AbstractCustomOperator
from . import Program as AstorProgram


class StmtDeletion(AbstractCustomOperator):
    """
    StmtDeletion: Delete x (Actually, Replace x with an empty statement)
    """
    def __str__(self):
        return "StmtDeletion({})".format(self.x)

    def is_valid_for(self, program):
        return isinstance(program, AstorProgram)

    @property
    def x(self):
        """
        Delete **x**

        :return: The file path and the index of modification point to be deleted.
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
        :return: ``[StmtReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        from .atomic_operator import StmtReplacement
        return [StmtReplacement(self.x, None)]

    @classmethod
    def create(cls, program, stmt_file=None, method='random'):
        """
        :param program: The program instance to which the created custom operator will be applied.
        :type program: :py:class:`.Program`
        :param str stmt_file: stmt is the target statement to delete.
          If stmt_file is specified, the target statement will be chosen within that file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The StmtDeletion instance with the randomly-selected modification point.
        :rtype: :py:class:`.custom_operator.StmtDeletion`
        """
        import random
        stmt_file = stmt_file or random.choice(program.target_files)
        stmt = (
            stmt_file,
            program.select_modification_point(stmt_file, method)
        )
        return cls(stmt)

class StmtMoving(AbstractCustomOperator):
    """
    StmtMoving: Move x [before|after] y
    """
    def __str__(self):
        return "StmtMoving({}, {}, '{}')".format(self.y, self.x, self.direction)

    def is_valid_for(self, program):
        return isinstance(program, AstorProgram)

    @property
    def x(self):
        """
        Move **x** [before|after] y

        :return: The file path and the index of ingredient statement to be moved.
        :rtype: tuple(str, int)
        """
        return self.args[1]

    @property
    def y(self):
        """
        Move x [before|after] **y**

        :return: The file path and the index of modification point.
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
        :return: ``[StmtInsertion(self.y, self.x, self.direction), StmtReplacement(self.x, None)]``
        :rtype: list(:py:class:`.atomic_operator.AtomicOperator`)
        """
        from .atomic_operator import StmtInsertion, StmtReplacement
        return [StmtInsertion(self.y, self.x, self.direction), StmtReplacement(self.x, None)]

    @classmethod
    def create(cls, program, stmt_file=None, ingr_file=None, direction='before', method='random'):
        """
        :param program: The program instance to which the created custom operator will be applied.
        :type program: :py:class:`.Program`
        :param str stmt_file: stmt means the modification point of the edit.
          If stmt_file is specified, the statement will be chosen within that file.
        :param str ingr_file: Ingredient is the statement to be moved.
          If ingr_file is specified, the ingredient statement will be chosen within that file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The StmtMoving instance with the randomly-selected stmt & ingr.
        :rtype: :py:class:`.custom_operator.StmtMoving`
        """
        import random
        stmt_file = stmt_file or random.choice(program.target_files)
        ingr_file = ingr_file or random.choice(program.target_files)
        stmt = (
            stmt_file,
            program.select_modification_point(stmt_file, method)
        )
        ingredient = (
            ingr_file,
            program.select_modification_point(ingr_file, 'random')
        )
        return cls(ingredient, stmt, direction)
