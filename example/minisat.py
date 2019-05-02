"""
Improving non-functional properties ::

    python improve_xml.py ../sample/Triangle_fast_xml
"""
import argparse
import os
import random
import re
import subprocess
import sys
from pyggi.base import Patch, ParseError, AbstractProgram, StatusCode
from pyggi.tree import XmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving
from pyggi.algorithms import LocalSearch

from improve_srcml import MyXmlEngine

COUNTER_BEFORE = ['break', 'continue', 'decl_stmt', 'empty_stmt', 'expr_stmt', 'goto', 'return', 'switch']
COUNTER_BLOCK = ['do', 'for', 'if', 'while']
COUNTER_BLOCK_STOP = ['block', 'then', 'else']

STMT_IGNORE = ['argument', 'argument_list', 'block', 'call', 'case', 'comment', 'condition', 'constructor', 'control', 'decl', 'default', 'destructor', 'directive', 'else', 'elseif', 'elseif_if', 'endif', 'expr', 'file', 'function', 'ifdef', 'ifndef', 'include', 'incr', 'index', 'init', 'label', 'literal', 'member_init_list', 'modifier', 'name', 'operator', 'parameter', 'parameter_list', 'public', 'specifier', 'struct', 'ternary', 'then', 'type']
STMT_RENAME = {
    'stmt': ['break', 'continue', 'decl_stmt', 'do', 'empty_stmt', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while']
}

INSTANCES = [
    ['cca_2_4_2_5.cnf', 'cca_2_4_3_8.cnf', 'cca_2_5_3_11.cnf', 'cca_2_5_3_12.cnf', 'cca_2_5_4_17.cnf', 'cca_2_6_4_22.cnf', 'cca_2_6_4_26.cnf', 'cca_2_6_4_27.cnf', 'cca_2_7_3_13.cnf', 'cca_2_7_4_24.cnf', 'cca_3_11_2_12.cnf', 'cca_3_4_2_9.cnf', 'cca_3_4_3_27.cnf', 'cca_3_4_3_28.cnf', 'cca_3_4_3_29.cnf', 'cca_3_5_2_11.cnf', 'cca_4_5_2_17.cnf', 'cca_5_7_2_44.cnf'],
    ['cca_2_15_2_6.cnf', 'cca_2_4_2_4.cnf', 'cca_2_5_3_10.cnf', 'cca_2_5_3_9.cnf', 'cca_3_11_2_11.cnf', 'cca_3_4_2_6.cnf', 'cca_3_4_3_21.cnf', 'cca_3_4_3_24.cnf', 'cca_3_4_3_26.cnf', 'cca_3_5_2_8.cnf', 'cca_3_5_2_9.cnf', 'cca_4_5_2_14.cnf', 'cca_4_5_2_15.cnf', 'cca_4_6_2_17.cnf', 'cca_4_6_2_19.cnf', 'cca_5_6_2_28.cnf', 'cca_5_6_2_31.cnf'],
    ['cca_2_6_4_21.cnf', 'cca_2_6_4_28.cnf', 'cca_2_6_4_29.cnf', 'cca_2_7_4_23.cnf', 'cca_2_7_4_26.cnf', 'cca_2_7_4_28.cnf', 'cca_2_9_4_28.cnf', 'cca_3_12_2_15.cnf', 'cca_3_6_4_65.cnf', 'cca_4_12_2_24.cnf', 'cca_4_5_3_83.cnf', 'cca_4_5_3_84.cnf', 'cca_5_7_2_42.cnf', 'cca_5_7_2_43.cnf', 'cca_5_7_2_45.cnf'],
    ['cca_3_6_4_59.cnf', 'cca_3_6_4_61.cnf', 'cca_3_6_4_63.cnf', 'cca_4_12_2_19.cnf', 'cca_4_12_2_20.cnf', 'cca_4_12_2_21.cnf', 'cca_4_12_2_22.cnf', 'cca_4_12_2_23.cnf', 'cca_4_5_3_76.cnf', 'cca_5_7_2_38.cnf', 'cca_5_7_2_39.cnf'],
    ['cca_2_6_4_20.cnf', 'cca_2_7_3_11.cnf', 'cca_2_9_3_11.cnf', 'cca_3_6_3_30.cnf', 'cca_3_6_4_66.cnf', 'cca_3_6_4_67.cnf', 'cca_3_6_4_68.cnf', 'cca_4_12_2_25.cnf', 'cca_4_12_2_28.cnf', 'cca_4_5_3_77.cnf', 'cca_4_5_3_79.cnf', 'cca_4_5_3_82.cnf', 'cca_5_8_2_54.cnf']
]

class MinisatEngine(MyXmlEngine):
    @classmethod
    def get_contents(cls, file_path):
        tree = XmlEngine.get_contents(file_path)
        cls.add_stmt_counter(tree)
        cls.remove_tags(tree, STMT_IGNORE)
        for tag in STMT_RENAME:
            cls.rewrite_tags(tree, STMT_RENAME[tag], tag)
        cls.rotate_newlines(tree)
        return tree

    # @classmethod
    # def get_tags(cls, element, accu=[]):
    #     accu.append(element.tag)
    #     for child in element:
    #         cls.get_tags(child, accu)
    #     return set(accu)

    @classmethod
    def add_stmt_counter(cls, root):
        # aux_block: add counter to each child block-like
        def aux_block(element):
            if element.tag in COUNTER_BLOCK_STOP:
                if element.text and element.text[0] == '{':
                    element.text = '{/*block*/ Log_count64++; ' + element.text[1:]
                else:
                    element.text = (element.text or '') + ' {/*block*/ Log_count64++; '
                    if len(element) == 0:
                        element.text = (element.text or '') + ' /*block*/}'
                    else:
                        element[-1].tail = (element[-1].tail or '') + ' /*block*/}'
        # aux_rec: recursively add counters
        def aux_rec(element):
            for child in element:
                aux_rec(child)
            if element.tag in COUNTER_BLOCK:
                for child in element:
                    aux_block(child)
            elif element.tag in COUNTER_BEFORE:
                element.text = '/*before*/ Log_count64++; ' + (element.text or '')
        # main: define counter and call aux_rec
        root.text = '#include <cstdint>\nextern int64_t Log_count64;\n\n' + (root.text or '')
        for child in root:
            aux_rec(child)

class MyProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        return MinisatEngine

    def load_config(self, path, config):
        self.test_command = './run.sh'
        self.target_files = ['core/Solver.C.xml']
        self.instances = list(map(random.choice, INSTANCES))
        self.truth_table = {}
        self.base_fitness = None

    def evaluate_patch(self, patch, timeout=15):
        cwd = os.getcwd()
        self.apply(patch)
        try:
            # compile it
            os.chdir(os.path.join(self.tmp_path, 'simp'))
            try:
                sprocess = subprocess.Popen('make', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = sprocess.communicate(timeout=timeout)
                if sprocess.returncode and sprocess.returncode > 0:
                    return StatusCode.PARSE_ERROR, 'COMPILE' # COMPILE_ERROR?
            except subprocess.TimeoutExpired:
                sprocess.kill()
                return StatusCode.TIME_OUT, 'COMPILE' # COMPILE_TIMEOUT?

            os.chdir('..')
            # run it
            outputs = []
            for inst in self.instances:
                try:
                    sprocess = subprocess.Popen([os.path.join('.', 'simp', 'minisat'), os.path.join(cwd, '..', 'sat_cit', inst)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = sprocess.communicate(timeout=timeout)
                    try:
                        if (sprocess.returncode == 10) != self.truth_table[inst]:
                            return StatusCode.PARSE_ERROR, 'FAIL' # OUTPUT_ERROR?
                    except KeyError:
                        print('TRUTH:', inst, 'is', ('SAT' if sprocess.returncode == 10 else 'UNSAT'))
                        self.truth_table[inst] = (sprocess.returncode == 10)
                    try:
                        fit = self.compute_fitness(0, stdout.decode('ascii'), stderr.decode('ascii'))
                        outputs.append(fit)
                    except ParseError:
                        return StatusCode.PARSE_ERROR, 'RUN'
                except subprocess.TimeoutExpired:
                    sprocess.kill()
                    return StatusCode.TIME_OUT, 'RUN'
        finally:
            os.chdir(cwd)

        # return fitness
        fitness = sum(outputs)
        if self.base_fitness is None:
            self.base_fitness = fitness
            print('BASE_FITNESS:', fitness)
        print('FITNESS:', fitness, fitness-self.base_fitness, 100*fitness/self.base_fitness)
        return StatusCode.NORMAL, fitness-self.base_fitness

    def compute_fitness(self, elapsed_time, stdout, stderr):
        try:
            m = re.search(r'^Log_count64: (\d+)', stdout, re.M)
            if m:
                return int(m.group(1))
            raise ParseError
        except:
            raise ParseError

class MyLocalSearch(LocalSearch):
    def get_neighbour(self, patch):
        if len(patch) > 0 and random.random() < 0.5:
            patch.remove(random.randrange(0, len(patch)))
        else:
            edit_operator = random.choice([StmtDeletion, StmtInsertion, StmtReplacement])
            patch.add(edit_operator.create(self.program))
        return patch

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('project_path', type=str, default='../sample/Triangle_fast')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()

    program = MyProgram(args.project_path)
    local_search = MyLocalSearch(program)
    result = local_search.run(warmup_reps=1, epoch=args.epoch, max_iter=args.iter, timeout=15)
    print("======================RESULT======================")
    print(result)
    program.remove_tmp_variant()
