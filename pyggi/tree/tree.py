import os
import ast
import astor
import random
from abc import abstractmethod
from . import AstorEngine, XmlEngine
from ..base import AbstractProgram, AbstractEdit
from ..utils import get_file_extension

class TreeProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        extension = get_file_extension(file_name)
        if extension in ['.py']:
            return AstorEngine
        elif extension in ['.xml']:
            return XmlEngine
        else:
            raise Exception('{} file is not supported'.format(extension))

"""
Possible Edit Operators
"""

class TreeEdit(AbstractEdit):
    @property
    def domain(self):
        return TreeProgram


class BadApiEdit(AbstractEdit):
    def __init__(self, target, ingredient, direction=''):
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

class StmtStackEdit(TreeEdit):
    def __init__(self, target):
        self.target = target

    def find_tag(self, program):
        tfile, tpt = target
        return program.contents[tfile].find(program.modification_points[tfile][tpt]).tag

    @classmethod
    def stack_push(cls, program, stacks, target):
        tag = find_tag(program, target)
        if tag not in stacks:
            stacks.update({tag: []})
        stacks[tag].append(target)

    @classmethod
    def stack_pop(cls, program, stacks, target):
        tag = find_tag(program, target)
        if tag not in stacks:
            stacks.update({tag: []})
            return None
        return stacks[tag].pop()

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        return cls(program.random_target(target_file, method))

class StmtStackDelete(StmtStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        engine = program.engines[self.target[0]]
        engine.do_delete(program, self, new_contents, modification_points)

class StmtStackCopy(StmtStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        self.stack_push(program, stacks, self.target)

class StmtStackCut(StmtStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        self.stack_push(program, stacks, self.target)
        engine = program.engines[self.target[0]]
        engine.do_delete(program, self, new_contents, modification_points)

class StmtStackPaste(StmtStackEdit):
    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        paste_cls = random.choose([StmtStackPasteBefore, StmtStackPasteAt, StmtStackPasteAfter])
        return paste_cls(program.random_target(target_file, method))

class StmtStackPasteBefore(StmtStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        target = self.stack_pop(program, stacks, self.target)
        if target:
            engine = program.engines[target[0]]
            # TODO: fix API
            op = BadApiEdit(target, self.target, 'before')
            engine.do_insert(program, op, new_contents, modification_points)

class StmtStackPasteAt(StmtStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        target = self.stack_pop(program, stacks, self.target)
        if target:
            engine = program.engines[target[0]]
            # TODO: fix API
            op = BadApiEdit(target, self.target)
            engine.do_replace(program, self, new_contents, modification_points)

class StmtStackPasteAfter(StmtStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        target = self.stack_pop(program, stacks, self.target)
        if target:
            engine = program.engines[target[0]]
            # TODO: fix API
            op = BadApiEdit(target, self.target, 'after')
            engine.do_insert(program, self, new_contents, modification_points)


class StmtReplacement(TreeEdit):
    def __init__(self, target, ingredient):
        self.target = target
        self.ingredient = ingredient

    def apply(self, program, new_contents, modification_points, stacks):
        engine = program.engines[self.target[0]]
        return engine.do_replace(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'))

class StmtInsertion(TreeEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points, stacks):
        engine = program.engines[self.target[0]]
        return engine.do_insert(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)

class StmtDeletion(TreeEdit):
    def __init__(self, target):
        self.target = target

    def apply(self, program, new_contents, modification_points, stacks):
        engine = program.engines[self.target[0]]
        return engine.do_delete(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        return cls(program.random_target(target_file, method))

class StmtMoving(TreeEdit):
    def __init__(self, target, ingredient, direction='before'):
        assert direction in ['before', 'after']
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

    def apply(self, program, new_contents, modification_points, stacks):
        engine = program.engines[self.target[0]]
        engine.do_insert(program, self, new_contents, modification_points)
        return engine.do_delete(program, self, new_contents, modification_points)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, direction=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        if ingr_file is None:
            ingr_file = program.random_file(engine=program.engines[target_file])
        assert program.engines[target_file] == program.engines[ingr_file]
        if direction is None:
            direction = random.choice(['before', 'after'])
        return cls(program.random_target(target_file, method),
                   program.random_target(ingr_file, 'random'),
                   direction)
