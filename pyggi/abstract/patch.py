from . import AbstractEdit

class Patch:
    def __init__(self):
        self.edits = []

    def __str__(self):
        return ' | '.join(list(map(str, self.edits)))

    def __len__(self):
        return len(self.edits)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(str(self))

    def alter(self, software):
        for edit in self.edits:
            assert isinstance(edit, AbstractEdit)
            edit.alter(software)
