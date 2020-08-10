#from moneta.trace import Tag
#import pprint
#import sys
#import os
##pprint.pprint(sys.path)
#from moneta import utils
import vaex
import pytest
import csv
from moneta.settings import MONETA_TOOL_DIR
from moneta.trace import Tag

# scope=module, function, class, package, session
@pytest.fixture()
def mock_df():
    #print("starting to open file")
    return vaex.open(MONETA_TOOL_DIR+'tests/data/trace_sorting_small.hdf5')

@pytest.fixture
def mock_tags():
    tags = []
    #print("here")
    #pprint.pprint(sys.path)
    #print(os.getcwd())
    with open(MONETA_TOOL_DIR+'tests/data/tag_map_sorting_small.csv') as f:
        rows = csv.DictReader(f)
        for row in rows:
            tags.append(Tag(row))
    return tags
 
