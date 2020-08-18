#from moneta.trace import Tag
#import pprint
#import sys
#import os
##pprint.pprint(sys.path)
#from moneta import utils
import vaex
import pytest
import uuid
import csv
from moneta.settings import MONETA_BASE_DIR
from moneta.trace import Tag
from moneta.utils import run_pintool

# scope=module, function, class, package, session
@pytest.fixture()
def mock_df():
    #print("starting to open file")
    return vaex.open(MONETA_BASE_DIR+'tests/data/trace_sorting_small.hdf5')

@pytest.fixture
def mock_tags():
    tags = []
    #print("here")
    #pprint.pprint(sys.path)
    #print(os.getcwd())
    with open(MONETA_BASE_DIR+'tests/data/tag_map_sorting_small.csv') as f:
        rows = csv.DictReader(f)
        for row in rows:
            tags.append(Tag(row))
    return tags

@pytest.fixture(scope='module')
def mock_working_dir():
    return MONETA_BASE_DIR+"tests/data/"

@pytest.fixture(scope='class')
def mock_executable():
    return "sorting"+uuid.uuid4().hex

@pytest.fixture
def mock_widget_inputs(mock_executable, mock_working_dir):
    return {
            'c_lines': 16,
            'c_block': 64,
            'm_lines': 10,
            'cwd_path': mock_working_dir,
            'e_file': mock_executable,
            'e_args': '',
            'o_name': mock_executable,
            'is_full_trace': False
           }

 
