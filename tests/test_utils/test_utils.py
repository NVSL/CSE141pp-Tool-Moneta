import pytest
import os

import moneta.utils as u
from moneta.settings import OUTPUT_DIR
import os.path

class TestUtils:
    @pytest.mark.parametrize("input_, expected", 
            [
                ("1", "./1"), 
                ("2", "./2"),
                ("/", "/"),
                ("home", "./home"),
                ("~", "~"),
                ("./", "."),
                ("examples/", "./examples"),
            ])
    def test_basic_parse_cwd(self, input_, expected):
        assert u.parse_cwd(input_) == expected


class TestWidgetFactories:
    def test_button_factory(self):
        btn = u.button_factory("desc")
        assert btn.description == "desc"
        assert btn.style.button_color == 'lightgray'
        return

    def test_int_text_factory(self):
        int_text = u.int_text_factory(100, "desc")
        assert int_text.description == "desc"
        assert int_text.value == 100
        assert int_text.style is not None
        assert int_text.disabled == False

    def test_int_text_factory_invalid_value(self):
        int_text = u.int_text_factory("100", "desc")
        assert int_text.value == 100
        with pytest.raises(Exception):
            int_text = u.int_text_factory("hello", "desc")

    def test_text_factory(self):
        text = u.text_factory("placeholder", "desc")
        assert text.value == ""
        assert text.placeholder == "placeholder"
        assert text.description == "desc"
        assert text.style is not None

class TestRunPintool:
    def get_file_names(self, name):
        return [
            OUTPUT_DIR + "trace_" + name + ".hdf5",
            OUTPUT_DIR + "tag_map_" + name + ".csv",
            OUTPUT_DIR + "meta_data_" + name + ".txt"
        ]
    def check_file_exists(self, name):
        return os.path.exists(name)

    def delete_file(self, name):
        if os.path.exists(name):
            os.remove(name)

    def test_run_pintool_basic(self, mock_widget_inputs):
        mock_widget_inputs['e_file'] = './sorting'
        u.run_pintool(mock_widget_inputs)
        files = self.get_file_names(mock_widget_inputs['o_name'])
        for f in files:
            assert self.check_file_exists(f)
            self.delete_file(f)
        assert self.check_file_exists(OUTPUT_DIR + "cwd_history")
