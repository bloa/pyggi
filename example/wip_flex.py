import argparse
import copy
import random
from pyggi.base import Patch
from pyggi.line import LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore
from pyggi.line import LineProgram, Line2Program

class MyProgram(LineProgram):
    def test(self):
        return random.random() < 1/(1+len(self.patch))

    def run(self):
        return int(10000000*random.random())

class MyProgram2(Line2Program):
    def test(self):
        return random.random() < 1/(1+len(self.patch))

    def run(self):
        return int(10000000*random.random())

EDITS = [LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--alter', default=False, action='store_true')
    args = parser.parse_args()

    prog = MyProgram2 if args.alter else MyProgram
    software = prog({'path': '.', 'target_files': ['wip_flex.py']})

    for k in range(len(EDITS)):
        soft = copy.deepcopy(software)
        edit = EDITS[k].create(soft)
        print('===== {} ====='.format(edit))
        edit.alter(soft)
        print(soft)
        print()

    for k in range(2, 5):
        patch = Patch()
        soft = copy.deepcopy(software)
        for i in range(k):
            edit = random.choice(EDITS).create(soft)
            patch.edits.append(edit)
        print('===== {}-edit patch ====='.format(len(patch)))
        print(patch)
        print('------------------------')
        soft.apply(patch)
        print(soft)
        print()
