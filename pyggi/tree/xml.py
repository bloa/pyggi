import copy
import os
import re
from xml.etree import ElementTree
from . import TreeSoftware

class XmlProgram(TreeSoftware):
    def parse(self, path):
        def aux(accu, prefix, root):
            tags = dict()
            for child in root:
                if child.tag in tags:
                    tags[child.tag] += 1
                else:
                    tags[child.tag] = 1
                s = '{}/{}[{}]'.format(prefix, child.tag, tags[child.tag])
                accu.append(s)
                accu = aux(accu, s, child)
            return accu

        self.contents = {}
        self.modification_points = {}
        for target in self.config['target_files']:
            _, extension = os.path.splitext(target)
            assert(extension ==  '.xml')
            with open(os.path.join(path, target)) as target_file:
                self.contents[target] = self.string_to_tree(target_file.read())
            self.modification_points[target] = aux([], '.', self.contents[target])

    def synthetise(self, target):
        return self.strip_xml_from_tree(self.contents[target])

    def write(self, path):
        os.makedirs(path, exist_ok=True)
        for target in self.config['target_files']:
            with open(os.path.join(path, target[:-4]), 'w') as target_file:
                target_file.write(self.synthetise(target))

    @staticmethod
    def strip_xml_from_tree(tree):
        return ''.join(tree.itertext())

    @staticmethod
    def strip_xml_from_string(content):
        tree = ElementTree.fromstring(content)
        return Program.strip_xml_from_tree(tree)

    @staticmethod
    def tree_to_string(tree):
        return ElementTree.tostring(tree, encoding='unicode', method='xml')
        pass

    @staticmethod
    def string_to_tree(s):
        xml = re.sub(r'\s+xmlns="[^"]+"', '', s, count=1)
        try:
            return ElementTree.fromstring(xml)
        except ElementTree.ParseError as e:
            raise Exception('Program', 'ParseError: {}'.format(str(e))) from None

    def do_delete_tree(self, target):
        target_file, target_point = target
        target_path = self.modification_points[target_file][target_point]
        target_parent_path = self.modification_points[target_file][target_point]+'..'
        target_element = self.contents[target_file].find(target_path)
        target_parent_element = self.contents[target_file].find(target_parent_path)
        if None in [target_element, target_parent_element]:
            return
        if target_element.tail:
            last_child = None
            for child in target_parent_element:
                if child == target_element:
                    if last_child is not None:
                        if last_child.tail:
                            last_child.tail += target_element.tail
                        else:
                            last_child.tail = target_element.tail
                    else:
                        if target_parent_element.text:
                            target_parent_element.text += target_element.tail
                        else:
                            target_parent_element.text = target_element.tail
                    break
                else:
                    last_child = child
        target_parent_element.remove(target_element)
        # TODO: modification points

    def do_replace_tree(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        target_path = self.modification_points[target_file][target_point]
        ingredient_path = self.modification_points[ingredient_file][ingredient_point]
        target_element = self.contents[target_file].find(target_path)
        ingredient_element = self.contents[ingredient_file].find(ingredient_path)
        if None in [target_element, ingredient_element]:
            return
        tmp = target_element.tail
        target_element.clear() # to remove children
        target_element.tag = ingredient_element.tag
        target_element.attrib = ingredient_element.attrib
        target_element.text = ingredient_element.text
        target_element.tail = tmp
        for child in ingredient_element:
            target_element.append(copy.deepcopy(child))

    def do_swap_tree(self, target, ingredient):
        target_file, target_point = target
        ingredient_file, ingredient_point = ingredient
        target_path = self.modification_points[target_file][target_point]
        ingredient_path = self.modification_points[ingredient_file][ingredient_point]
        target_element = self.contents[target_file].find(target_path)
        ingredient_element = self.contents[ingredient_file].find(ingredient_path)
        if None in [target_element, ingredient_element]:
            return
        target_copy = copy.deepcopy(target_element)
        target_copy_children = list()
        for child in target_element:
            target_copy_children.append(child)
        target_element.clear() # to remove children
        target_element.tag = ingredient_element.tag
        target_element.attrib = ingredient_element.attrib
        target_element.text = ingredient_element.text
        target_element.tail = target_copy.tail
        for child in ingredient_element:
            target_element.append(child)
        tmp = ingredient_element.tail
        ingredient_element.clear() # to remove children
        ingredient_element.tag = target_copy.tag
        ingredient_element.attrib = target_copy.attrib
        ingredient_element.text = target_copy.text
        ingredient_element.tail = tmp
        for child in target_copy_children:
            ingredient_element.append(child)

    def do_insert_tree_before(self, target, ingredient):
        pass
