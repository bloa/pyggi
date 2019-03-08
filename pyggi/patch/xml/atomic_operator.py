import copy
import random
# import re
from ..abstract import AbstractAtomicOperator
from . import Program as XmlProgram

class XmlAtomicOperator(AbstractAtomicOperator):
    def __init__(self, target, ingredient=None):
        self.target = target
        self.ingredient = ingredient

    @property
    def modification_point(self):
        return self.target

    def is_valid_for(self, program):
        return isinstance(program, XmlProgram)

class XmlReplacement(XmlAtomicOperator):
    def __str__(self):
        return "XmlReplacement({}, {})".format(self.target, self.ingredient)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        target_file = target_file or random.choice(program.target_files)
        target = (target_file, program.select_modification_point(target_file, method))
        ingr_file = ingr_file or random.choice(program.target_files)
        ingredient = (ingr_file, program.select_modification_point(ingr_file, method))
        return cls(target, ingredient)

    def apply(self, program, new_contents, modification_points):
        target_data = new_contents[self.target[0]]
        target_pos = modification_points[self.target[0]][self.target[1]]
        target_element = target_data.find(target_pos)
        ingredient_data = new_contents[self.ingredient[0]]
        ingredient_pos = modification_points[self.ingredient[0]][self.ingredient[1]]
        ingredient_element = ingredient_data.find(ingredient_pos)
        # replace xml
        result = self.do_replace(target_element, ingredient_element)
        if not result:
            return False
        # update modification points
        # ???
        return True

    @staticmethod
    def do_replace(target_element, ingredient_element):
        if None in [target_element, ingredient_element]:
            return False
        tmp = target_element.tail
        target_element.clear() # to remove children
        target_element.tag = ingredient_element.tag
        target_element.attrib = ingredient_element.attrib
        target_element.text = ingredient_element.text
        target_element.tail = tmp
        for child in ingredient_element:
            target_element.append(copy.deepcopy(child))
        return True

class TagReplacement(XmlReplacement):
    def __str__(self):
        return "TagReplacement({}, {})".format(self.target, self.ingredient)

    @staticmethod
    def do_replace(target_element, ingredient_element):
        if None in [target_element, ingredient_element]:
            return False
        target_element.tag = ingredient_element.tag
        target_element.attrib = ingredient_element.attrib
        target_element.text = ingredient_element.text
        if len(target_element) > 0:
            *_, last_subchild = target_element
            if len(ingredient_element) > 0:
                *_, last_subchild2 = ingredient_element
                last_subchild.tail = last_subchild2.tail
            else:
                last_subchild.tail = None
        return True

class XmlDeletion(XmlAtomicOperator):
    def __str__(self):
        return "XmlDeletion({})".format(self.target)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        target_file = target_file or random.choice(program.target_files)
        target = (target_file, program.select_modification_point(target_file, method))
        return cls(target)

    def apply(self, program, new_contents, modification_points):
        target_data = new_contents[self.target[0]]
        target_pos = modification_points[self.target[0]][self.target[1]]
        target_element = target_data.find(target_pos)
        parent_element = target_data.find(target_pos+'..')
        # delete xml element
        result = self.do_delete(parent_element, target_element)
        if not result:
            return False
        # update modification points
        # ???
        return True

    @staticmethod
    def do_delete(parent_element, target_element):
        if None in [parent_element, target_element]:
            return False
        if target_element.tail:
            last_child = None
            for child in parent_element:
                if child == target_element:
                    if last_child is not None:
                        if last_child.tail:
                            last_child.tail += target_element.tail
                        else:
                            last_child.tail = target_element.tail
                    else:
                        if parent_element.text:
                            parent_element.text += target_element.tail
                        else:
                            parent_element.text = target_element.tail
                    break
                else:
                    last_child = child
        parent_element.remove(target_element)
        return True

class TagDeletion(XmlDeletion):
    def __str__(self):
        return "TagDeletion({})".format(self.target)

    @staticmethod
    def do_delete(parent_element, target_element):
        if None in [parent_element, target_element]:
            return False
        if not target_element in parent_element:
            print("------")
            print(XmlProgram.tree_to_string(parent_element))
            print("------")
            print(XmlProgram.tree_to_string(target_element))
            print("------")
        if len(target_element) > 0:
            *_, last_subchild = target_element
            last_subchild.tail = target_element.tail
            target_element.tail = None
        last_child = None
        pos = 0
        for child in parent_element:
            if child == target_element:
                if len(target_element) > 0:
                    for subchild in target_element:
                        parent_element.insert(pos, copy.deepcopy(subchild))
                        pos += 1
                if target_element.tail:
                    if last_child is not None:
                        if last_child.tail:
                            last_child.tail += target_element.tail
                        else:
                            last_child.tail = target_element.tail
                    else:
                        if parent_element.text:
                            parent_element.text += target_element.tail
                        else:
                            parent_element.text = target_element.tail
                break
            else:
                last_child = child
                pos += 1
        parent_element.remove(target_element)
        return True

class XmlInsertion(XmlAtomicOperator):
    def __init__(self, target, ingredient, mode):
        self.target = target
        self.ingredient = ingredient
        self.mode = mode

    def __str__(self):
        return "XmlInsertion({}, {})".format(self.target, self.ingredient)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        target_file = target_file or random.choice(program.target_files)
        target = (target_file, program.select_modification_point(target_file, method))
        ingr_file = ingr_file or random.choice(program.target_files)
        ingredient = (ingr_file, program.select_modification_point(ingr_file, method))
        mode = 'inside' if (random.random() < 0.5) else 'after'
        return cls(target, ingredient, mode)

    def apply(self, program, new_contents, modification_points):
        target_data = new_contents[self.target[0]]
        target_pos = modification_points[self.target[0]][self.target[1]]
        parent, tag, pos = XmlProgram.xpath_split(target_pos)
        if self.mode == 'after':
            target_element = target_data.find(target_pos)
            parent_element = target_data.find(parent)
        else:
            target_element = None
            parent_element = target_data.find(target_pos)
        ingredient_data = new_contents[self.ingredient[0]]
        ingredient_pos = modification_points[self.ingredient[0]][self.ingredient[1]]
        ingredient_element = ingredient_data.find(ingredient_pos)
        # insert xml
        result = self.do_insert(parent_element, target_element, ingredient_element)
        if not result:
            return False
        # update modification points
        # ???
        return True

    @staticmethod
    def do_insert(parent_element, target_element, ingredient_element):
        if None in [parent_element, ingredient_element]:
            return False
        if target_element is not None:
            true_pos = 0
            last_child = None
            for child in parent_element:
                true_pos += 1
                if child == target_element:
                    break
                else:
                    last_child = child
            else:
                return False
            element = copy.deepcopy(ingredient_element)
            element.tail = target_element.tail
            target_element.tail = None
            parent_element.insert(true_pos, element)
        else:
            element = copy.deepcopy(ingredient_element)
            element.tail = None
            parent_element.insert(0, element)
        return True

class TagInsertion(XmlAtomicOperator):
    def __str__(self):
        return "TagInsertion({}, {})".format(self.target, self.ingredient)

    @classmethod
    def create(cls, program, target_file=None, ingr_file=None, method='random'):
        target_file = target_file or random.choice(program.target_files)
        target = (target_file, program.select_modification_point(target_file, method))
        ingr_file = ingr_file or random.choice(program.target_files)
        ingredient = (ingr_file, program.select_modification_point(ingr_file, method))
        return cls(target, ingredient)

    def apply(self, program, new_contents, modification_points):
        target_data = new_contents[self.target[0]]
        target_pos = modification_points[self.target[0]][self.target[1]]
        parent = XmlProgram.xpath_parent(target_pos)
        target_element = target_data.find(target_pos)
        parent_element = target_data.find(parent)
        ingredient_data = new_contents[self.ingredient[0]]
        ingredient_pos = modification_points[self.ingredient[0]][self.ingredient[1]]
        ingredient_element = ingredient_data.find(ingredient_pos)
        # insert xml
        result = self.do_insert(parent_element, target_element, ingredient_element)
        if not result:
            return False
        # update modification points
        # ???
        return True

    @staticmethod
    def do_insert(parent_element, target_element, ingredient_element):
        if None in [parent_element, target_element, ingredient_element]:
            return False
        if not target_element in parent_element:
            return False
        element = copy.deepcopy(ingredient_element)
        element.tail = target_element.tail
        for child in reversed(element):
            element.remove(child)
        element.insert(0, target_element)
        if len(ingredient_element) > 0:
            *_, last_child = ingredient_element
            target_element.tail = last_child.tail
        else:
            target_element.tail = None
        for pos, child in enumerate(parent_element):
            if child == target_element:
                parent_element.remove(child)
                parent_element.insert(pos, element)
                return True
        else:
            assert False

class XmlMoving(XmlAtomicOperator):
    def __init__(self, target, ingredient, mode):
        self.target = target
        self.ingredient = ingredient
        self.mode = mode

    def __str__(self):
        return "XmlMoving({}, {})".format(self.target, self.ingredient)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        target_file = target_file or random.choice(program.target_files)
        target = (target_file, program.select_modification_point(target_file, method))
        ingredient = (target_file, program.select_modification_point(target_file, method))
        mode = 'inside' if (random.random() < 0.5) else 'after'
        return cls(target, ingredient, mode)

    def apply(self, program, new_contents, modification_points):
        target_data = new_contents[self.target[0]]
        target_pos = modification_points[self.target[0]][self.target[1]]
        parent_target = XmlProgram.xpath_parent(target_pos)
        if self.mode == 'after':
            target_element = target_data.find(target_pos)
            parent_target_element = target_data.find(parent_target)
        else:
            target_element = None
            parent_target_element = target_data.find(target_pos)
        ingredient_pos = modification_points[self.target[0]][self.ingredient[1]]
        parent_ingredient = XmlProgram.xpath_parent(ingredient_pos)
        ingredient_element = target_data.find(ingredient_pos)
        parent_ingredient_element = target_data.find(parent_ingredient)
        # insert xml
        result = self.do_move(parent_target_element, target_element, parent_ingredient_element, ingredient_element)
        if not result:
            return False
        # update modification points
        # ???
        return True

    @staticmethod
    def do_move(parent_target_element, target_element, parent_ingredient_element, ingredient_element):
        result = XmlInsertion.do_insert(parent_target_element, target_element, ingredient_element)
        if not result:
            return False
        result = XmlDeletion.do_delete(parent_ingredient_element, ingredient_element)
        assert result
        return True

class TagMoving(XmlAtomicOperator):
    def __str__(self):
        return "TagMoving({}, {})".format(self.target, self.ingredient)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        target_file = target_file or random.choice(program.target_files)
        target = (target_file, program.select_modification_point(target_file, method))
        ingredient = (target_file, program.select_modification_point(target_file, method))
        return cls(target, ingredient)

    def apply(self, program, new_contents, modification_points):
        target_data = new_contents[self.target[0]]
        target_pos = modification_points[self.target[0]][self.target[1]]
        parent_target = XmlProgram.xpath_parent(target_pos)
        target_element = target_data.find(target_pos)
        parent_target_element = target_data.find(parent_target)
        ingredient_pos = modification_points[self.target[0]][self.ingredient[1]]
        parent_ingredient = XmlProgram.xpath_parent(ingredient_pos)
        ingredient_element = target_data.find(ingredient_pos)
        parent_ingredient_element = target_data.find(parent_ingredient)
        # insert xml
        result = self.do_move(parent_target_element, target_element, parent_ingredient_element, ingredient_element)
        if not result:
            return False
        # update modification points
        # ???
        return True

    @staticmethod
    def do_move(parent_target_element, target_element, parent_ingredient_element, ingredient_element):
        if target_element == ingredient_element:
            return True
        result = TagInsertion.do_insert(parent_target_element, target_element, ingredient_element)
        if not result:
            return False
        result = TagDeletion.do_delete(parent_ingredient_element, ingredient_element)
        assert result
        return True

class XmlSwap(XmlAtomicOperator):
    def __str__(self):
        return "XmlSwap({}, {})".format(self.target, self.ingredient)

    @classmethod
    def create(cls, program, target_file=None, method='random'):
        target_file = target_file or random.choice(program.target_files)
        target = (target_file, program.select_modification_point(target_file, method))
        ingredient = (target_file, program.select_modification_point(target_file, method))
        return cls(target, ingredient)

    def apply(self, program, new_contents, modification_points):
        target_data = new_contents[self.target[0]]
        target_pos = modification_points[self.target[0]][self.target[1]]
        target_element = target_data.find(target_pos)
        ingredient_pos = modification_points[self.target[0]][self.ingredient[1]]
        ingredient_element = target_data.find(ingredient_pos)
        # swap
        result = self.do_swap(target_element, ingredient_element)
        if not result:
            return False
        # update modification points
        # ???
        return True

    @staticmethod
    def do_swap(target_element, ingredient_element):
        tmp_element = copy.deepcopy(target_element)
        result = XmlReplacement.do_replace(target_element, ingredient_element)
        if not result:
            return False
        result = XmlReplacement.do_replace(ingredient_element, tmp_element)
        assert result
        return True

class TagSwap(XmlSwap):
    def __str__(self):
        return "TagSwap({}, {})".format(self.target, self.ingredient)

    @staticmethod
    def do_swap(target_element, ingredient_element):
        tmp_element = copy.deepcopy(target_element)
        result = TagReplacement.do_replace(target_element, ingredient_element)
        if not result:
            return False
        result = TagReplacement.do_replace(ingredient_element, tmp_element)
        assert result
        return True
