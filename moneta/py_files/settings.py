## Input Fields

# Cache Lines
CACHE_LINES_VAL = 4096
CACHE_LINES_DESC = "Cache Lines:"

# Cache Block size
CACHE_BLOCK_VAL = 64
CACHE_BLOCK_DESC = "Block Size (Bytes):"

# Output Lines
OUTPUT_LINES_VAL = 10000000
OUTPUT_LINES_DESC = "Lines to Output:"

# Working Directory Path
CWD_PATH_DEF = "e.g. ./Examples/build"
CWD_PATH_DESC = "Working Directory:"

# Executable Path
EXEC_PATH_DEF = "e.g. ./sorting"
EXEC_PATH_DESC = "Executable Path:"

# Trace Name
TRACE_NAME_DEF = "e.g. baseline"
TRACE_NAME_DESC = "Name for Trace:"

# Full Trace
FULL_TRACE_DESC = "Trace everything (Ignore program tags)?"

# Select Multiple
SELECT_MULTIPLE_DESC = "Trace:"

## Buttons

# Generate
GENERATE_DESC = "Generate Trace"
GENERATE_COLOR = 'darkseagreen'

# Load
LOAD_DESC = "Load Trace"
LOAD_COLOR = 'lightblue'

# Delete
DELETE_DESC = "Delete Trace"
DELETE_COLOR = 'salmon'

import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)
log = logging.getLogger(__name__)

from matplotlib.colors import ListedColormap
from ipywidgets import Layout
import numpy as np
import os

# Colormap
newc = np.ones((11, 4))
newc[1] = [0, 0, 1, 1] # read_hits - 1, .125
newc[2] = [0, 153/255, 204/255, 1] # write_hits - 2, .25
newc[3] = [0.047, 1, 0, 1] # cache_size
newc[4] = [1, .5, 0, 1] # read_misses - 3, .375
newc[5] = [1, 0, 0, 1] # write_misses - 4, .5
newc[6] = [0.5, 0.3, 0.1, 1] # compulsory read misses - 5, .625
newc[8] = [0.745, 0.309, 0.235, 1] # compulsory write misses - 6, .75
CUSTOM_CMAP = ListedColormap(newc)


BUTTON_LAYOUT = Layout(margin='15px 15px 0px 15px',
        height='40px', width='90%', border='1px solid black')
MONETA_BASE_DIR = os.path.expanduser("~") + "/work/"
MONETA_TOOL_DIR = os.path.expanduser("~") + "/work/moneta"
OUTPUT_DIR = MONETA_BASE_DIR + "moneta/.output/"
PIN_PATH  = "/pin/pin.sh"
TOOL_PATH = MONETA_BASE_DIR + ".setup/trace_tool.so"
WIDGET_DESC_PROP = {'description_width': '200px'}
WIDGET_LAYOUT = Layout(width='90%')

# Errors
NO_TAGS = "No tags were traced"

## Vaex

INDEX_LABEL = "Access Number"

# Pintool Enumerations
COMP_W_MISS = 6
COMP_R_MISS = 5
WRITE_MISS = 4
READ_MISS = 3
WRITE_HIT = 2
READ_HIT = 1
