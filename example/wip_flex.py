from pyggi.abstract import AbstractSoftware, AbstractEdit, Patch
from pyggi.algorithms import IteratedLocalSearch, GeneticProgramming, TabuSearch
from pyggi.granularity import LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore
from pyggi.implem import LineProgram, Line2Program
from random import random, choice
from copy import deepcopy
import argparse

class MyProgram(LineProgram):
    def test(self):
        return random() < 1/(1+len(self.patch))

    def run(self):
        return int(10000000*random())

class MyProgram2(Line2Program):
    def test(self):
        return random() < 1/(1+len(self.patch))

    def run(self):
        return int(10000000*random())

EDITS = [LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--alter', default=False, action='store_true')
    args = parser.parse_args()

    prog = MyProgram2 if args.alter else MyProgram
    software = prog({'path': '.', 'target_files': ['wip_flex.py']})

    for k in range(len(EDITS)):
        soft = deepcopy(software)
        edit = EDITS[k].create(soft)
        print('===== {} ====='.format(edit))
        edit.alter(soft)
        print(soft)
        print()

    for k in range(2, 5):
        patch = Patch()
        soft = deepcopy(software)
        for i in range(k):
            edit = choice(EDITS).create(soft)
            patch.edits.append(edit)
        print('===== {}-edit patch ====='.format(len(patch)))
        print(patch)
        print('------------------------')
        soft.apply(patch)
        print(soft)
        print()
