import pytest

import moneta.utils as u

class TestUtils:
    @pytest.mark.parametrize("input_, expected", 
            [
                ("1", "./1"), 
                ("2", "./2"),
                ("/", "/"),
                ("home", "./home"),
                ("~", "~"),
                ("./", "."),
                ("Examples/", "./Examples"),
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
    def test_run_pintool_basic(self, mock_executable, mock_working_dir):
        cache_lines = 10
        cache_block_size = 16
        output_limit = 10
        u.run_pintool(
                cache_lines,
                cache_block_size,
                output_limit,
                mock_working_dir,
                mock_executable,
                "",
                mock_executable[2:],
                False
                )
        pass
