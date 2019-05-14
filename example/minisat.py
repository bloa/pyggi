import argparse
import os
import random
import re
import subprocess
import sys
import time
from pyggi.base import Patch, ParseError, AbstractProgram, StatusCode
from pyggi.tree import XmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion, StmtMoving
from pyggi.algorithms import LocalSearch

from improve_srcml import MyXmlEngine

COUNTER_BEFORE = ['break', 'continue', 'decl_stmt', 'empty_stmt', 'expr_stmt', 'goto', 'return', 'switch']
COUNTER_BLOCK = ['do', 'for', 'if', 'while']
COUNTER_BLOCK_STOP = ['block', 'then', 'else']

STMT_IGNORE_1 = ['argument', 'argument_list', 'block', 'call', 'case', 'comment', 'constructor', 'decl', 'default', 'destructor', 'directive', 'else', 'elseif', 'endif', 'expr', 'file', 'function', 'ifdef', 'ifndef', 'include', 'incr', 'index', 'init', 'label', 'literal', 'member_init_list', 'modifier', 'name', 'operator', 'parameter', 'parameter_list', 'public', 'specifier', 'struct', 'ternary', 'then', 'type']
STMT_IGNORE_2 = ['control']
STMT_RENAME = {
    'stmt': ['break', 'continue', 'decl_stmt', 'do', 'empty_stmt', 'expr_stmt', 'for', 'goto', 'if', 'return', 'switch', 'while']
}

INSTANCES = [
    ['cca_2_4_2_5.cnf', 'cca_2_5_3_11.cnf', 'cca_2_5_3_12.cnf', 'cca_2_5_4_17.cnf', 'cca_2_6_4_22.cnf', 'cca_2_6_4_26.cnf', 'cca_2_6_4_27.cnf', 'cca_2_7_3_13.cnf', 'cca_2_7_4_24.cnf', 'cca_3_11_2_12.cnf', 'cca_3_4_2_9.cnf', 'cca_3_4_3_27.cnf', 'cca_3_4_3_28.cnf', 'cca_3_4_3_29.cnf', 'cca_3_5_2_11.cnf', 'cca_4_5_2_17.cnf', 'cca_5_7_2_44.cnf'],
    ['cca_2_15_2_6.cnf', 'cca_2_4_2_4.cnf', 'cca_2_4_3_8.cnf', 'cca_2_5_3_10.cnf', 'cca_2_5_3_9.cnf', 'cca_3_11_2_11.cnf', 'cca_3_4_2_6.cnf', 'cca_3_4_3_21.cnf', 'cca_3_4_3_24.cnf', 'cca_3_4_3_26.cnf', 'cca_3_5_2_8.cnf', 'cca_3_5_2_9.cnf', 'cca_4_5_2_14.cnf', 'cca_4_5_2_15.cnf', 'cca_4_6_2_17.cnf', 'cca_4_6_2_19.cnf', 'cca_5_6_2_28.cnf', 'cca_5_6_2_31.cnf'],
    ['cca_2_6_4_21.cnf', 'cca_2_6_4_28.cnf', 'cca_2_6_4_29.cnf', 'cca_2_7_4_23.cnf', 'cca_2_7_4_26.cnf', 'cca_2_7_4_28.cnf', 'cca_2_9_4_28.cnf', 'cca_3_12_2_15.cnf', 'cca_3_6_4_65.cnf', 'cca_4_12_2_24.cnf', 'cca_4_5_3_83.cnf', 'cca_4_5_3_84.cnf', 'cca_5_7_2_42.cnf', 'cca_5_7_2_43.cnf', 'cca_5_7_2_45.cnf'],
    ['cca_3_6_4_59.cnf', 'cca_3_6_4_61.cnf', 'cca_3_6_4_63.cnf', 'cca_4_12_2_19.cnf', 'cca_4_12_2_20.cnf', 'cca_4_12_2_21.cnf', 'cca_4_12_2_22.cnf', 'cca_4_12_2_23.cnf', 'cca_4_5_3_76.cnf', 'cca_5_7_2_38.cnf', 'cca_5_7_2_39.cnf'],
    ['cca_2_6_4_20.cnf', 'cca_2_7_3_11.cnf', 'cca_2_9_3_11.cnf', 'cca_3_6_3_30.cnf', 'cca_3_6_4_66.cnf', 'cca_3_6_4_67.cnf', 'cca_3_6_4_68.cnf', 'cca_4_12_2_25.cnf', 'cca_4_12_2_28.cnf', 'cca_4_5_3_77.cnf', 'cca_4_5_3_79.cnf', 'cca_4_5_3_82.cnf', 'cca_5_8_2_54.cnf']
]

class MinisatEngine(MyXmlEngine):
    @classmethod
    def get_contents(cls, file_path):
        tree = XmlEngine.get_contents(file_path)
        cls.add_stmt_counter(tree)
        cls.remove_tags(tree, STMT_IGNORE_1)
        cls.handle_conditions(tree)
        cls.remove_tags(tree, STMT_IGNORE_2)
        for tag in STMT_RENAME:
            cls.rewrite_tags(tree, STMT_RENAME[tag], tag)
        # cls.rotate_newlines(tree)
        return tree

    @classmethod
    def get_tags(cls, element, accu=[]):
        accu.append(element.tag)
        for child in element:
            cls.get_tags(child, accu)
        return set(accu)

    @classmethod
    # will fail on nested ternaries?
    def handle_conditions(cls, element, parent=None, brother=None):
        if element.tag == 'condition':
            m = re.match(r'^(.*?)(\s*[;?]?\s*)$', element.text)
            assert m
            if brother is not None:
                brother.tail = (brother.tail or '') + ' /*auto*/('
            else:
                parent.text = (parent.text or '') + ' /*auto*/('
            if m.group(1) != '':
                element.text = ' /*auto*/({})/*auto*/ ||'.format(m.group(1))
            else:
                element.text = '1 ||'
            element.tail = '0)/*auto*/ ' + m.group(2) + (element.tail or '')
        # else:
        elif element.tag != 'switch':
            last = None
            for child in element:
                cls.handle_conditions(child, element, last)
                last = child

    @classmethod
    def add_stmt_counter(cls, root):
        # aux_block: add counter to each child block-like
        def aux_block(element):
            if element.tag in COUNTER_BLOCK_STOP:
                if element.text and element.text[0] == '{':
                    element.text = '/*auto*/{ Log_count64++; ' + element.text[1:]
                else:
                    element.text = (element.text or '') + ' /*auto*/{ Log_count64++; '
                    if len(element) == 0:
                        element.text = (element.text or '') + ' }/*auto*/'
                    else:
                        element[-1].tail = (element[-1].tail or '') + ' }/*auto*/'
        # aux_rec: recursively add counters
        def aux_rec(element):
            for child in element:
                aux_rec(child)
            if element.tag in COUNTER_BLOCK:
                for child in element:
                    aux_block(child)
            elif element.tag in COUNTER_BEFORE:
                element.text = 'Log_count64++; ' + (element.text or '')
        # main: define counter and call aux_rec
        root.text = '#include <stdint.h>\nextern int64_t Log_count64;\n\n' + (root.text or '')
        for child in root:
            aux_rec(child)

class MyProgram(AbstractProgram):
    @classmethod
    def get_engine(cls, file_name):
        return MinisatEngine

    def load_config(self, path, config):
        self.test_command = './run.sh'
        self.target_files = ['core/Solver.C.xml']
        # self.instances = list(map(random.choice, INSTANCES))
        # self.instances = INSTANCES[0]
        # self.instances = INSTANCES[0][:5]
        draw = enumerate([5, 5, 2, 2, 1])
        self.instances = [inst for (i, k) in draw for inst in random.sample(INSTANCES[i], k)]
        self.instances_folder = os.path.join(os.getcwd(), '..', 'sat_cit')
        # self.instances = [inst for subset in INSTANCES for inst in subset]
        self.truth_table = {}
        self.base_fitness = None
        self.cache = {}
        self.compile_timeout = 10
        self.instance_timeout = 60

    def evaluate_patch(self, patch, timeout=15):
        # memoise run results
        key = str(patch)
        if key in self.cache:
            self.logger.debug('CACHED! ({})'.format(key))
            return self.cache[key]
        else:
            self.cache[key] = self._evaluate_patch(patch, timeout)
        return self.cache[key]

    def _evaluate_patch(self, patch, timeout=15):
        start = time.time()
        cwd = os.getcwd()
        self.apply(patch)
        try:
            # compile it
            os.chdir(os.path.join(self.tmp_path, 'simp'))
            try:
                sprocess = subprocess.Popen('make', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = sprocess.communicate(timeout=min(timeout,self.compile_timeout))
                if sprocess.returncode and sprocess.returncode > 0:
                    if self.base_fitness is None:
                        print(stderr.decode('utf8'))
                        assert False
                    self.logger.debug('COMPILE_ERROR')
                    return StatusCode.PARSE_ERROR, 'COMPILE' # COMPILE_ERROR?
            except subprocess.TimeoutExpired:
                sprocess.kill()
                self.logger.debug('COMPILE_TIMEOUT')
                return StatusCode.TIME_OUT, 'COMPILE' # COMPILE_TIMEOUT?

            os.chdir('..')
            # run it
            outputs = []
            for (i, inst) in enumerate(self.instances):
                try:
                    now = time.time()
                    budget = timeout + start - now
                    sprocess = subprocess.Popen([os.path.join('.', 'simp', 'minisat'), os.path.join(self.instances_folder, inst)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = sprocess.communicate(timeout=min(budget,self.instance_timeout))
                    if sprocess.returncode not in [10, 20]:
                        self.logger.debug('RUNTIME_ERROR({}/{},{})'.format(i, len(self.instances), inst))
                        return StatusCode.PARSE_ERROR, 'FAIL' # RUNTIME_ERROR?
                    try:
                        if (sprocess.returncode == 10) != self.truth_table[inst]:
                            self.logger.debug('OUTPUT_ERROR({}/{},{})'.format(i, len(self.instances), inst))
                            return StatusCode.PARSE_ERROR, 'FAIL' # OUTPUT_ERROR?
                    except KeyError:
                        self.logger.info('TRUTH: {} is {} in {}'.format(inst, ('SAT' if sprocess.returncode == 10 else 'UNSAT'), time.time() - now))
                        self.truth_table[inst] = (sprocess.returncode == 10)
                    try:
                        fit = self.compute_fitness(0, stdout.decode('ascii'), stderr.decode('ascii'))
                        outputs.append(fit)
                    except ParseError:
                        self.logger.debug('PARSE_ERROR({}/{},{})'.format(i, len(self.instances), inst))
                        return StatusCode.PARSE_ERROR, 'RUN'
                except subprocess.TimeoutExpired:
                    sprocess.kill()
                    if budget > self.instance_timeout:
                        self.logger.debug('INSTANCE_TIMEOUT({}/{},{})'.format(i, len(self.instances), inst))
                    else:
                        self.logger.debug('BUDGET_TIMEOUT({}/{},{})'.format(i, len(self.instances), inst))
                    return StatusCode.TIME_OUT, 'RUN'
        finally:
            os.chdir(cwd)

        # return fitness
        fitness = sum(outputs)
        if self.base_fitness is None:
            self.base_fitness = fitness
            self.logger.info('BASE_FITNESS: {}'.format(fitness))
        self.logger.debug('FITNESS: {} {} {} {}'.format(fitness, fitness-self.base_fitness, 100*fitness/self.base_fitness, time.time() - start))
        return StatusCode.NORMAL, fitness

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
            operator = random.choice([StmtDeletion, StmtInsertion, StmtReplacement])
            # ensure coherent edits
            edit = None
            while True:
                try:
                    edit = operator.create(self.program)
                    if edit.ingredient:
                        target_file, target_point = edit.target
                        ingredient_file, ingredient_point = edit.ingredient
                        target_tag = self.program.contents[target_file].find(program.modification_points[target_file][target_point]).tag
                        ingredient_tag = self.program.contents[ingredient_file].find(program.modification_points[ingredient_file][ingredient_point]).tag
                        if target_tag == ingredient_tag:
                            break
                except AttributeError:
                    break
            patch.add(edit)
        return patch

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('--seed', type=int, default=0)
    args = parser.parse_args()

    random.seed(args.seed)
    program = MyProgram('../sample/minisat')
    program.logger.debug('SEED: {}'.format(args.seed))
    # for filename in program.contents:
    #     print(MinisatEngine.get_tags(program.contents[filename]))
    # for filename in program.contents:
    #     print(XmlEngine.tree_to_string(program.contents[filename]))
    # for filename in program.contents:
    #     print(program.dump(program.contents, filename))
    # for filename in program.contents:
    #     for i, pt in enumerate(program.modification_points[filename]):
    #         print('--------------------------------------')
    #         print(filename, i, pt)
    #         print(program.get_source(filename, i))
    #         # print(XmlEngine.strip_xml_from_tree(program.contents[filename].find(pt)))
    local_search = MyLocalSearch(program)
    results = local_search.run(warmup_reps=1, epoch=1, max_iter=2000, timeout=60)
    program.logger.info("======================RESULT======================")
    for epoch in results:
        epoch['BestPatch'] = str(epoch['BestPatch'])
        program.logger.debug(epoch)
        program.logger.info('SEED {} FINAL: {}'.format(args.seed, epoch['BestPatch']))
    program.remove_tmp_variant()
