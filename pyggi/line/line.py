import os
import random
from abc import abstractmethod
from ..base import AbstractProgram, AbstractEdit
from .engine import LineEngine

class LineProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        return LineEngine

"""
Possible Edit Operators
"""
class LineEdit(AbstractEdit):
    @property
    def domain(self):
        return LineProgram


class BadApiEdit(AbstractEdit):
    def __init__(self, target, ingredient, direction=''):
        self.target = target
        self.ingredient = ingredient
        self.direction = direction

class LineStackEdit(LineEdit):
    def __init__(self, target):
        self.target = target

    def stack_push(self, stacks, target):
        if 'pyggi_line' not in stacks:
            stacks.update({'pyggi_line': []})
        stacks['pyggi_line'].append(self.target)

    def stack_pop(self, stacks):
        if 'pyggi_line' not in stacks:
            stacks.update({'pyggi_line': []})
            return None
        return stacks['pyggi_line'].pop()

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        return cls(program.random_target(target_file, method))

class LineStackDelete(LineStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        engine = program.engines[self.target[0]]
        engine.do_delete(program, self, new_contents, modification_points)

class LineStackCopy(LineStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        self.stack_push(stacks, self.target)

class LineStackCut(LineStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        self.stack_push(stacks, self.target)
        engine = program.engines[self.target[0]]
        engine.do_delete(program, self, new_contents, modification_points)

class LineStackPaste(LineStackEdit):
    @classmethod
    def create(cls, program, target_file=None, method='random'):
        if target_file is None:
            target_file = program.random_file()
        paste_cls = random.choose([LineStackPasteBefore, LineStackPasteAt, LineStackPasteAfter])
        return paste_cls(program.random_target(target_file, method))

class LineStackPasteBefore(LineStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        target = self.stack_pop(stacks)
        if target:
            engine = program.engines[target[0]]
            # TODO: fix API
            op = BadApiEdit(target, self.target, 'before')
            engine.do_insert(program, op, new_contents, modification_points)

class LineStackPasteAt(LineStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        target = self.stack_pop(stacks)
        if target:
            engine = program.engines[target[0]]
            # TODO: fix API
            op = BadApiEdit(target, self.target)
            engine.do_replace(program, self, new_contents, modification_points)

class LineStackPasteAfter(LineStackEdit):
    def apply(self, program, new_contents, modification_points, stacks):
        target = self.stack_pop(stacks)
        if target:
            engine = program.engines[target[0]]
            # TODO: fix API
            op = BadApiEdit(target, self.target, 'after')
            engine.do_insert(program, self, new_contents, modification_points)



class LineReplacement(LineEdit):
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

class LineInsertion(LineEdit):
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

class LineDeletion(LineEdit):
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

class LineMoving(LineEdit):
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
    def create(cls, program, target_file=None, ingr_file=None, direction='before', method='random'):
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
