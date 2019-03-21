import argparse
import copy
import inspect
import importlib
import json
import os
import random
import shutil
import signal
import subprocess
import sys
import time
from pyggi.algorithms import RandomSearch
from pyggi.base import AbstractSoftware
from pyggi.line import LineProgram, LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore
from pyggi.tree import AstorProgram, XmlProgram, TreeDeletion, TreeReplacement, TreeSwap, TreeInsertionBefore, TreeMoveBefore

# some toplevel constants
LINE_EDITS = [LineDeletion, LineReplacement, LineSwap, LineInsertionBefore, LineMoveBefore]
TREE_EDITS = [TreeDeletion, TreeReplacement, TreeSwap, TreeInsertionBefore, TreeMoveBefore]
JAVA_XML_DIR = '../sample/quixbugs/java_xml_programs'
JAVA_DIR = '../sample/quixbugs/java_programs'
PYTHON_DIR = '../sample/quixbugs/python_programs'
JSON_DIR = '../sample/quixbugs/json_testcases'

# the same algorithm for every scenario
class MyAlgo(RandomSearch):
    def setup(self):
        super().setup()
        self.config['dist_max'] = 3

    def stopping_condition(self):
        now = time.time()
        return self.fitness(self.best) == 0 or now > self.stats['wallclock_start'] + 5

    def mutate(self, sol):
        if len(sol) > 1 and random.random() > 0.5:
            sol.edits.pop(int(random.random()*len(sol)))
        else:
            sol.edits.append(random.choice(self.edits).create(self.software))
        return sol

# how to run python programs
class BasePythonProgram(AbstractSoftware):
    def test(self):
        (algo, _) = os.path.splitext(self.config['target_files'][0])
        # todo: change "/" to "." with re
        path = '{}.{}'.format(os.path.normpath(self.path), algo)
        try:
            self.fx = None
            if path in sys.modules:
                del sys.modules[path]
            module = importlib.__import__(path)
            # importlib.reload(module) # ???
            self.fx = getattr(getattr(module, algo), algo)
            # print(inspect.getsource(self.fx))
        except:
            return False
        return True

    def run(self):
        n = len(self.config['test_cases'])
        for test_case in self.config['test_cases']:
            test_input, test_output = copy.deepcopy(test_case)
            if not isinstance(test_input, list):
                test_input = [test_input]
            try:
                try:
                    sys.stdout = None
                    sys.stderr = None
                    signal.signal(signal.SIGALRM, lambda _,__: 1/0)
                    signal.setitimer(signal.ITIMER_REAL, 0.1)
                    if self.fx(*test_input) == test_output:
                        n -= 1
                    pass
                except Exception: # to catch errors
                    pass
            except Exception: # to catch timeouts
                pass
            finally:
                signal.alarm(0)
                sys.stdout = sys.__stderr__
                sys.stderr = sys.__stderr__
        return n

# how to run java programs
class BaseJavaProgram(AbstractSoftware):
    def test(self):
        cwd = os.getcwd()
        try:
            os.chdir(self.path)
            try:
                javafile = self.config['target_files'][0]
                if javafile[-4:] == '.xml':
                    javafile = javafile[:-4]
                sprocess = subprocess.Popen(["/usr/bin/javac", javafile, '-Xlint:unchecked'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = sprocess.communicate(timeout=2)
                return sprocess.returncode == 0
            except subprocess.TimeoutExpired:
                return False
            finally:
                if sprocess.poll():
                    sprocess.terminate()
                    sprocess.wait()
        finally:
            os.chdir(cwd)

    def run(self):
        cwd = os.getcwd()
        n = len(self.config['test_cases'])
        try:
            os.chdir(self.path)
            os.mkdir('./java_programs')
            javafile = self.config['target_files'][0]
            if javafile[-4:] == '.xml':
                javafile = javafile[:-4]
            shutil.copy(javafile[:-5]+'.class', 'java_programs')
            for test_case in self.config['test_cases']:
                test_input, test_output = copy.deepcopy(test_case)
                if not isinstance(test_input, list):
                    test_input = [test_input]
                try:
                    sprocess = subprocess.Popen(["/usr/bin/java", "-cp", "gson-2.8.2.jar:.", "JavaDeserialization", javafile[:-5].lower()]+[json.dumps(arg) for arg in copy.deepcopy(test_input)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = sprocess.communicate(timeout=0.1)
                    if stdout.decode("ascii").rstrip() == str(test_output):
                        n -= 1
                except subprocess.TimeoutExpired:
                    pass
                finally:
                    if sprocess.poll():
                        sprocess.terminate()
                        sprocess.wait()
        finally:
            os.chdir(cwd)
        return n

# program mixins
# could probably be donne better...
class PythonLineProgram(BasePythonProgram, LineProgram):
    pass
class PythonTreeProgram(BasePythonProgram, AstorProgram):
    pass
class JavaLineProgram(BaseJavaProgram, LineProgram):
    pass
class JavaTreeProgram(BaseJavaProgram, XmlProgram):
    pass

# the main repair function
def repair(jsonfile, bugfile, program_cls, edits, path):
    print('===== {} ====='.format(bugfile))
    content = open('../sample/quixbugs/json_testcases/{}'.format(jsonfile), 'r')
    acc = list()
    for line in content:
        acc.append(json.loads(line))

    config = {
        'path': path,
        'target_files': [bugfile],
        'test_cases': acc,
    }

    software = program_cls(config)
    algo = MyAlgo(software)
    algo.edits = edits
    algo.run()

    print(algo.stats)
    print()
    if algo.fit_dominates(algo.best, algo.initial):
        soft = copy.deepcopy(software)
        algo.best.alter(soft)
        return (
            bugfile,
            algo.best,
            algo.fitness(algo.initial),
            software.synthetise(bugfile),
            algo.fitness(algo.best),
            soft.synthetise(bugfile),
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', type=str, default='python')
    parser.add_argument('--mode', type=str, default='line')
    parser.add_argument('--target', type=str, default='gcd')
    args = parser.parse_args()

    json_files = os.listdir(JSON_DIR)
    success = list()
    target = args.target+'.json'
    for filename in json_files:
        (basename, _) = os.path.splitext(filename)
        if args.target != '' and basename != args.target:
            continue
        if args.lang == 'java':
            if args.mode == 'line':
                tmp = repair(filename, '{}.java'.format(basename.upper()),
                             JavaLineProgram, LINE_EDITS, JAVA_DIR)
            elif args.mode == 'tree':
                tmp = repair(filename, '{}.java.xml'.format(basename.upper()),
                             JavaTreeProgram, TREE_EDITS, JAVA_XML_DIR)
            else:
                print('invalid java mode ({})'.format(args.mode))
                exit(1)
        elif args.lang == 'python':
            if args.mode == 'line':
                tmp = repair(filename, '{}.py'.format(basename),
                             PythonLineProgram, LINE_EDITS, PYTHON_DIR)
            elif args.mode == 'tree':
                tmp = repair(filename, '{}.py'.format(basename),
                             PythonTreeProgram, TREE_EDITS, PYTHON_DIR)
            else:
                print('invalid python mode ({})'.format(args.mode))
                exit(1)
        else:
            print('error: invalid lang ({})'.format(repr(args.lang)))
            exit(1)
        if tmp is not None:
            success.append(tmp)
    print()

    for filename, best, fit1, soft1, fit2, soft2 in success:
        print('=====================')
        print('{}: {} --> {}'.format(filename, fit1, fit2))
        print(best)
        print('----------')
        print(soft1)
        print('----------')
        print(soft2)
        print()
