import pytest
from pathlib import Path
import moneta.utils as u

INCORRECT_VAL = "randomtest"

class TestVerifyWidgetValues:
    @pytest.fixture(autouse=True, scope='class')
    def setup_executable(self, mock_working_dir, mock_executable):
        Path(mock_working_dir + mock_executable).touch(mode=0o777)
        yield
        Path(mock_working_dir + mock_executable).unlink()

    @pytest.mark.parametrize("cache_lines, e0",
            [
                (1, True),
                (0, False),
                (-1, False),
                (100000000, True),
                (-100000000, False),
            ])
    @pytest.mark.parametrize("cache_block, e1",
            [
                (1, True),
                (0, False),
                (-1, False),
                (100000000, True),
                (-100000000, False),
            ])
    @pytest.mark.parametrize("output_lines, e2",
            [
                (1, True),
                (0, False),
                (-1, False),
                (100000000, True),
                (-100000000, False),
            ])
    def test_numerical_inputs(self, mock_widget_inputs, 
            cache_lines, e0,
            cache_block, e1,
            output_lines, e2
        ):
        mock_widget_inputs['c_lines'] = cache_lines
        mock_widget_inputs['c_block'] = cache_block
        mock_widget_inputs['m_lines'] = output_lines
        assert u.verify_input(mock_widget_inputs) == (e0 and e1 and e2)

    def test_incorrect_cwd_path(self, mock_widget_inputs):
        mock_widget_inputs['cwd_path'] = INCORRECT_VAL
        assert u.verify_input(mock_widget_inputs) == False

    @pytest.mark.parametrize("cwd_path, expected",
            [
                (".", "."),
                ("..","~/work"),
                ("/", "/"),
                ("~","~"),
                ("~/work/moneta","."),
                ("/home/jovyan/work", "~/work"),
                ("/home/jovyan/work/setup", "~/work/setup"),
                ("/home/jovyan", "~"),
                ("~/work/../", "~"),
                ("~/work/../../", "/home"),
                ("~/work/../work/../work", "~/work"),
                ("examples/src", "examples/src"),
                ("examples/", "examples"),
                ("~/work/moneta/examples", "examples"),
                ("examples/../../moneta/examples/src", "examples/src"),
                ("/home/jovyan/work/moneta/examples/../../moneta/examples/src", "examples/src"),
                ("../../", "~"),
                ("    ../../      ", "~"),
            ])
    def test_cwd_path_parsing(self, mock_widget_inputs, cwd_path, expected):
        mock_widget_inputs['cwd_path'] = cwd_path
        u.verify_input(mock_widget_inputs)
        assert mock_widget_inputs['display_path'] == expected

    def test_executable_file(self, mock_widget_inputs):
        mock_widget_inputs['e_file'] = INCORRECT_VAL # File not found
        assert u.verify_input(mock_widget_inputs) == False

    #TODO - Test arguments

    @pytest.mark.parametrize("output_name, expected",
            [
                ("output", True),
                ("", False),
                ("~", False),
                ("reallylongnameforoutputname", True),
                ("output_with_underscores", True),
                ("/", False),
                ("\\", False),
                ("\"", False),
                ("!", False),
                ("@", False),
                ("#", False),
                ("\t", False),
            ])
    def test_output_name(self, mock_widget_inputs, output_name, expected):
        mock_widget_inputs['o_name'] = output_name
        assert u.verify_input(mock_widget_inputs) == expected

    def test_full_trace(self, mock_widget_inputs):
        mock_widget_inputs['is_full_trace'] = False
        assert u.verify_input(mock_widget_inputs) == True
        mock_widget_inputs['is_full_trace'] = True
        assert u.verify_input(mock_widget_inputs) == True
