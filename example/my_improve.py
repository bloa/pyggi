"""
Improving non-functional properties ::

    python improve.py ../sample/Triangle_fast
"""
import sys
import random
import argparse
from pyggi.patch import Patch
from pyggi.algorithms import LegacySearch as LocalSearch


class MyLocalSearch(LocalSearch):
    def set_operators(self, l):
        assert len(l) > 0
        self.operators = l

    def get_neighbour(self, patch):
        if len(patch) > 0 and random.random() < 0.1:
            patch.remove(random.randrange(0, len(patch)))
        else:
            edit_operator = random.choice(self.operators)
            patch.add(edit_operator.create(self.program))
        return patch

    def get_fitness(self, patch):
        return float(patch.test_result.custom['runtime'])

    def is_valid_patch(self, patch):
        return patch.test_result.compiled and patch.test_result.custom['pass_all'] == 'true'

    def stopping_criterion(self, iter, patch):
        return float(patch.test_result.custom['runtime']) < 0.01

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('project_path', type=str, default='../sample/Triangle_fast')
    parser.add_argument('--epoch', type=int, default=30,
                        help='total epoch (default: 30)')
    parser.add_argument('--iter', type=int, default=100,
                        help='total iterations per epoch (default: 100)')
    parser.add_argument('--line', action='store_true', default=None)
    parser.add_argument('--ast', action='store_true', default=None)
    parser.add_argument('--xml', action='store_true', default=None)
    args = parser.parse_args()

    if args.ast:
        from pyggi.patch.astor import Program
        from pyggi.patch.astor import StmtReplacement, StmtInsertion, StmtDeletion
        ops = [StmtDeletion, StmtInsertion, StmtReplacement]
    elif args.xml:
        from pyggi.patch.xml import Program
        from pyggi.patch.xml import TagReplacement, TagDeletion, TagInsertion, TagMoving, TagSwap
        from pyggi.patch.xml import XmlReplacement, XmlDeletion, XmlInsertion, XmlMoving, XmlSwap
        ops = [TagReplacement, TagDeletion, TagInsertion, TagMoving, TagSwap,
               XmlReplacement, XmlDeletion, XmlInsertion, XmlMoving, XmlSwap]
    else:
        from pyggi.patch.line import Program
        from pyggi.patch.line import LineReplacement, LineInsertion, LineDeletion
        ops = [LineDeletion, LineInsertion, LineReplacement]

    program = Program(args.project_path)
    local_search = MyLocalSearch(program)
    local_search.set_operators(ops)
    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter,
                              timeout=15)
    for epoch in result:
        print ("Epoch #{}".format(epoch))
        for key in result[epoch]:
            print ("- {}: {}".format(key, result[epoch][key]))
