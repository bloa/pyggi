import os
import re
from xml.etree import ElementTree
from ..abstract import AbstractProgram

class Program(AbstractProgram):
    @property
    def modification_points(self):
        """
        :return: The list of position of modification points for each target program
        :rtype: dict(str, ?)
        """
        if self._modification_points:
            return self._modification_points

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

        self._modification_points = dict()
        for target_file in self.target_files:
            tree = self.contents[target_file]
            points = aux([], '.', tree)
            self._modification_points[target_file] = points
        return self._modification_points

    def print_modification_points(self, target_file, indices=None):
        title_format = "=" * 25 + " {}: {} {} " + "=" * 25
        contents = self.contents[target_file]
        points = self.modification_points[target_file]
        if not indices:
            indices = range(len(points))
        for i in indices:
            print(title_format.format(target_file, 'xpath', i, points[i]))
            print(points[i])
            print(self.to_source(contents.find(points[i])).rstrip())
            print()

    def to_source(self, contents_of_file):
        return Program.tree_to_string(contents_of_file)

    @staticmethod
    def strip_xml_from_tree(tree):
        return ''.join(tree.itertext())

    @staticmethod
    def strip_xml_from_string(content):
        tree = ElementTree.fromstring(content)
        return Program.strip_xml_from_tree(tree)

    def parse(self, path, target_files):
        contents = {}
        for target in target_files:
            with open(os.path.join(path, target)) as f:
                contents[target] = Program.string_to_tree(f.read())
        return contents

    @staticmethod
    def string_to_tree(s):
        xml = re.sub(r'\s+xmlns="[^"]+"', '', s, count=1)
        try:
            return ElementTree.fromstring(xml)
        except ElementTree.ParseError as e:
            raise Exception('Program', 'ParseError: ({}) {}'.format(target, str(e))) from None

    @staticmethod
    def tree_to_string(tree):
        return ElementTree.tostring(tree, encoding='unicode', method='xml')

    @staticmethod
    def xpath_to_tag(xpath):
        if xpath == '.':
            return '.'
        pattern = re.compile(r'^(.*)/([^\[]+)(?:\[([^\]]+)\])?$')
        match = re.match(pattern, xpath)
        assert match
        return match.group(2)

    @staticmethod
    def xpath_parent(xpath):
        if xpath == '.':
            return '.'
        pattern = re.compile(r'^(.*)/([^\[]+)(?:\[([^\]]+)\])?$')
        match = re.match(pattern, xpath)
        assert match
        return match.group(1)

    @staticmethod
    def xpath_split(xpath):
        assert xpath != '.'
        pattern = re.compile(r'^(.*)/([^\[]+)(?:\[([^\]]+)\])?$')
        match = re.match(pattern, xpath)
        assert match
        return (match.group(1), match.group(2), int(match.group(3)))
