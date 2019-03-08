import os
from ..abstract import AbstractProgram

class Program(AbstractProgram):
    def __str__(self):
        code = ''
        for k in sorted(self.contents.keys()):
            for idx, line in enumerate(self.contents[k]):
                code += "{}\t: {}\t: {}\n".format(k, idx, line)
        return code

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
            self._modification_points[target_file] = list(range(len(self.contents[target_file])))
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
            print(title_format.format(target_file, 'line', i))
            print(contents[points[i]])
            print()

    def to_source(self, contents_of_file):
        """
        Change contents of file to the source code

        :type granularity_level: :py:class:`GranularityLevel`
        :param contents_of_file: The contents of the file which is the parsed form of source code
        :type contents_of_file: ?
        :return: The source code
        :rtype: str
        """
        return '\n'.join(contents_of_file) + '\n'

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
            with open(os.path.join(path, target), 'r') as target_file:
                contents[target] = list(
                    map(str.rstrip, target_file.readlines()))
        return contents
