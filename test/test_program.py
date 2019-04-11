import pytest
import os
from pyggi.line import LineProgram as Program


@pytest.fixture(scope='session')
def setup():
    program = Program('./resource/Triangle_bug')
    assert len(program.target_files) == 1
    assert program.target_files[0] == 'Triangle.java'

    return program


class TestProgram(object):

    def test_init(self, setup):
        program = setup

        assert not program.path.endswith('/')
        assert program.name == os.path.basename(program.path)
        assert program.test_command is not None
        assert program.target_files is not None

    def test_tmp_path(self, setup):
        program = setup

        assert program.tmp_path.startswith(os.path.join(program.TMP_DIR, program.name))

    def test_create_tmp_variant(self, setup):
        program = setup
        os.mkdir(os.path.join(program.tmp_path, 'test_dir'))
        program.create_tmp_variant()

        assert os.path.exists(program.tmp_path)

    def test_load_contents(self, setup):
        program = setup
        assert 'Triangle.java' in program.contents
        assert len(program.contents['Triangle.java']) > 0