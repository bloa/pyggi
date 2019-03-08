import os
import ast
import astor
from ..abstract import AbstractProgram
from . import stmt_python

class Program(AbstractProgram):
    @property
    def modification_points(self):
        """
        :return: The list of position of modification points for each target program
        :rtype: dict(str, ?)
        """
        if self._modification_points:
            return self._modification_points

        self._modification_points = dict()
        for target_file in self.target_files:
            self._modification_points[target_file] = stmt_python.get_modification_points(
                self.contents[target_file])
        return self._modification_points

    def print_modification_points(self, target_file, indices=None):
        """
        Print the source of each modification points

        :param target_file: The path to target file
        :type target_file: str
        :return: None
        :rtype: None
        """
        title_format = "=" * 25 + " {}: {} {} " + "=" * 25
        contents = self.contents[target_file]
        points = self.modification_points[target_file]
        if not indices:
            indices = range(len(points))
        for i in indices:
            print(title_format.format(target_file, 'node', i))
            print(points[i])
            blk, idx = stmt_python.pos_2_block_n_index(contents, points[i])
            print(astor.to_source(blk[idx]))

    def to_source(self, contents_of_file):
        """
        Change contents of file to the source code

        :type granularity_level: :py:class:`GranularityLevel`
        :param contents_of_file: The contents of the file which is the parsed form of source code
        :type contents_of_file: ?
        :return: The source code
        :rtype: str
        """
        return astor.to_source(contents_of_file)

    def parse(self, path, target_files):
        """
        :param granularity_level: The granularity level of a program
        :type granularity_level: :py:class:`.program.GranularityLevel`
        :param str path: The project root path
        :param target_files: The paths to target files from the project root
        :type target_files: list(str)

        :return: The contents of the files, see `Hint`
        :rtype: dict(str, list(str))

        .. hint::
            - key: the file name
            - value: the contents of the file
        """
        contents = {}
        for target in target_files:
            if Program.is_python_code(target):
                root = astor.parse_file(os.path.join(path, target))
                contents[target] = root
            else:
                raise Exception('Program', '{} file is not supported'.format(Program.get_file_extension(target)))
        return contents
