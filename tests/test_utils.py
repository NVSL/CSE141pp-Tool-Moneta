import pytest

from moneta.utils import parse_cwd

class TestUtils:
    @pytest.mark.parametrize("input_, expected", 
            [
                ("1", "./1"), 
                ("2", "./2"),
                ("/", "/"),
                ("home", "./home"),
                ("~", "~"),
            ])
    def test_basic_parse_cwd(self, input_, expected):
        assert parse_cwd(input_) == expected
