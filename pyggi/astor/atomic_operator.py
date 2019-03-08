"""

This module contains AbstractAtomicOperator class which is an abstact base class,
and several classes inherit the AbstractAtomicOperator class.

"""
import ast
import copy
import random
from ..abstract import AbstractAtomicOperator
from . import Program as AstorProgram
from . import stmt_python


class StmtReplacement(AbstractAtomicOperator):

    def __init__(self, stmt, ingredient=None):
        """
        :param stmt: The file path and the node # of statement which should be replaced
        :type stmt: tuple(str, int)
        :param ingredient: The file path and the node # of statement which is an ingredient
        :type ingredient: None or tuple(str, int)
        """
        super().__init__()
        assert isinstance(stmt[0], str)
        assert isinstance(stmt[1], int)
        assert stmt[1] >= 0
        if ingredient:
            assert isinstance(ingredient[0], str)
            assert isinstance(ingredient[1], int)
            assert ingredient[1] >= 0
        self.stmt = stmt
        self.ingredient = ingredient

    def __str__(self):
        """
        :return: ``StmtReplacement([stmt], [ingredient])``
        """
        return "StmtReplacement({}, {})".format(self.stmt, self.ingredient)

    @property
    def modification_point(self):
        return self.stmt

    def is_valid_for(self, program):
        return isinstance(program, AstorProgram)

    def apply(self, program, new_contents, modification_points):
        """"
        Apply the operator to the contents of program
        :param program: The original program instance
        :type program: :py:class:`.Program`
        :param new_contents: The new contents of program to which the edit will be applied
        :type new_contents: dict(str, ?)
        :param modification_points: The original modification points
        :type modification_points: list(int, )
        :return: success or not
        :rtype: bool
        """
        assert self.is_valid_for(program)
        dst_root = new_contents[self.stmt[0]]
        dst_pos = modification_points[self.stmt[0]][self.stmt[1]]
        if not self.ingredient:
            return stmt_python.replace((dst_root, dst_pos), self.ingredient)
        ingr_root = program.contents[self.ingredient[0]]
        ingr_pos = program.modification_points[self.ingredient[0]][self.ingredient[1]]
        return stmt_python.replace((dst_root, dst_pos), (ingr_root, ingr_pos))

    @classmethod
    def create(cls, program, stmt_file=None, ingr_file=None, del_rate=0, method='random'):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str stmt_file: stmt is the target statement to delete.
          If stmt_file is specified, the target statement will be chosen within that file.
        :param str ingr_file: Ingredient is the statement to be copied.
          If ingr_file is specified, the ingredient statement will be chosen within that file.
        :param float del_rate: The probability of ingredient will be None. ([0,1])
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The StmtReplacement instance with the randomly-selected properties:
          stmt and ingredient.
        :rtype: :py:class:`.atomic_operator.StmtReplacement`
        """
        assert del_rate >= 0 and del_rate <= 1
        stmt_file = stmt_file or random.choice(program.target_files)
        stmt = (stmt_file, program.select_modification_point(stmt_file, method))
        if random.random() < del_rate:
            ingredient = None
        else:
            ingr_file = ingr_file or random.choice(program.target_files)
            ingredient = (ingr_file, program.select_modification_point(ingr_file, 'random'))
        return cls(stmt, ingredient)


class StmtInsertion(AbstractAtomicOperator):

    def __init__(self, stmt, ingredient, direction='before'):
        """
        :param stmt: The file path and position of statement which is a target of modification
        :type stmt: tuple(str, list(tuple(str, int)))
        :param ingredient: The file path and the position of statement which will be inserted
        :type ingredient: None or tuple(str, list(tuple(str, int)))
        :param direction: *'before'* or *'after'*
        :type direction: str
        """
        super().__init__()
        assert isinstance(stmt[0], str)
        assert isinstance(stmt[1], int)
        assert stmt[1] >= 0
        assert isinstance(ingredient[0], str)
        assert isinstance(ingredient[1], int)
        assert ingredient[1] >= 0
        assert direction in ['before', 'after']
        self.stmt = stmt
        self.ingredient = ingredient
        self.direction = direction

    def __str__(self):
        """
        :return: ``StmtInsertion([line], [ingredient], [direction])``
        """
        return "StmtInsertion({}, {}, '{}')".format(self.stmt, self.ingredient, self.direction)

    @property
    def modification_point(self):
        return self.stmt

    def is_valid_for(self, program):
        return isinstance(program, AstorProgram)

    def apply(self, program, new_contents, modification_points):
        """
        Apply the operator to the contents of program

        :param program: The original program instance
        :type program: :py:class:`.Program`
        :param new_contents: The new contents of program to which the edit will be applied
        :type new_contents: dict(str, ?)
        :param modification_points: The original modification points
        :type modification_points: list(int, )
        :return: success or not
        :rtype: bool
        """
        assert self.is_valid_for(program)
        success = False
        dst_root = new_contents[self.stmt[0]]
        dst_pos = modification_points[self.stmt[0]][self.stmt[1]]
        ingr_root = program.contents[self.ingredient[0]]
        ingr_pos = stmt_python.get_modification_points(ingr_root)[self.ingredient[1]]
        if self.direction == 'before':
            success = stmt_python.insert_before((dst_root, dst_pos), (ingr_root, ingr_pos))
            if success:
                depth = len(dst_pos)
                parent = dst_pos[:depth-1]
                index = dst_pos[depth-1][1]
                for pos in modification_points[self.stmt[0]]:
                    if parent == pos[:depth-1] and len(pos) >= depth and index <= pos[depth-1][1]:
                        a, i = pos[depth-1]
                        pos[depth-1] = (a, i + 1)
        elif self.direction == 'after':
            success = stmt_python.insert_after((dst_root, dst_pos), (ingr_root, ingr_pos))
            if success:
                depth = len(dst_pos)
                parent = dst_pos[:depth-1]
                index = dst_pos[depth - 1][1]
                for pos in modification_points[self.stmt[0]]:
                    if parent == pos[:depth-1] and len(pos) >= depth and index < pos[depth-1][1]:
                        a, i = pos[depth-1]
                        pos[depth-1] = (a, i + 1)
        return success

    @classmethod
    def create(cls, program, stmt_file=None, ingr_file=None, direction='before', method='random'):
        """
        :param program: The program instance to which the random edit will be applied.
        :type program: :py:class:`.Program`
        :param str line_file: stmt means the modification point of the edit.
          If stmt_file is specified, the stmt will be chosen within that file.
        :param str ingr_file: Ingredient is the stmt to be copied.
          If ingr_file is specified, the target stmt will be chosen within that file.
        :param str method: The way of choosing the modification point. **'random'** or **'weighted'**
        :return: The StmtInsertion instance with the randomly-selected properties:
          stmt and ingredient.
        :rtype: :py:class:`.atomic_operator.StmtInsertion`
        """
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
        return cls(stmt, ingredient, direction)
