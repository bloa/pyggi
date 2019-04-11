import pytest
from pyggi.base import Patch, StatusCode
from pyggi.line import LineProgram as Program
from pyggi.line import LineDeletion, LineMoving, LineInsertion

@pytest.fixture(scope='session')
def setup():
    program = Program('./resource/Triangle_bug')
    assert len(program.target_files) == 1
    assert program.target_files[0] == 'Triangle.java'

    patch = Patch(program)
    return patch, program


class TestPatch(object):

    def test_init(self, setup):
        patch, program = setup

        assert patch.program == program
        assert len(patch.edit_list) == 0

    def test_str(self, setup):
        patch, program = setup

        assert ' | '.join(list(map(str, patch.edit_list))) == str(patch)

    def test_len(self, setup):
        patch, program = setup

        assert len(patch.edit_list) == len(patch)

    def test_eq(self, setup):
        patch, program = setup
        program2 = Program('./resource/Triangle_bug')
        patch2 = Patch(program2)

        assert patch == patch2

    def test_clone(self, setup):
        patch, program = setup
        cloned_patch = patch.clone()

        assert cloned_patch.program == patch.program
        assert cloned_patch == patch

    def test_add(self, setup):
        patch, program = setup
        deletion_operator = LineDeletion
        deletion_instance = deletion_operator.create(program)
        patch.add(deletion_instance)

        assert len(patch) == 1
        assert patch.edit_list[0] == deletion_instance

        moving_operator = LineMoving
        moving_instance = moving_operator.create(program)
        patch.add(moving_instance)

        assert len(patch) == 2
        assert patch.edit_list[1] == moving_instance

    def test_apply(self, setup):
        patch, program = setup

        assert True

    def test_run_test(self, setup):
        patch, program = setup
        status_code, fitness = program.evaluate_patch(patch)

        assert len(patch) > 0
        if status_code == StatusCode.NORMAL:
            assert fitness is not None
        else:
            assert fitness is None

    def test_remove(self, setup):
        patch, program = setup
        old_patch = patch.clone()
        patch.remove(0)

        assert len(patch) == len(old_patch) - 1
        assert patch.edit_list == old_patch.edit_list[1:]