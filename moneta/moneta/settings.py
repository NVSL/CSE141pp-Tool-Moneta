## Input Fields

# Cache Lines
CACHE_LINES_VAL = 4096
CACHE_LINES_DESC = "Cache Lines:"

# Cache Block size
CACHE_BLOCK_VAL = 64
CACHE_BLOCK_DESC = "Block Size (Bytes):"

# Output Lines
OUTPUT_LINES_VAL = 10000000
OUTPUT_LINES_DESC = "Max Accesses:"

# Working Directory Path
CWD_PATH_DEF = "e.g. ./examples/build"
CWD_PATH_DESC = "Working Directory (Optional):"
HISTORY_MAX = 5

# Executable Path
EXEC_PATH_DEF = "e.g. ./sorting"
EXEC_PATH_DESC = "Executable Path:"

# Trace Name
TRACE_NAME_DEF = "e.g. baseline"
TRACE_NAME_DESC = "Name for Trace:"

# Start Function
START_FUN_DEF = "main"
START_FUN_DESC = "Function to start trace at:"

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
from ipywidgets import Layout, HBox, VBox, Layout
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

# print() Text Colors
class TextStyle():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'



BUTTON_LAYOUT = Layout(margin='15px 15px 0px 15px',
        height='40px', width='100%', border='1px solid black')
TW_BOX_LAYOUT = Layout(display='flex',
                    flex_flow='row',
                    align_items='stretch',
                    width='100%')
TW_LAYOUT = Layout(flex='1 1 0%', width='100%')
MONETA_BASE_DIR = os.path.expanduser("~") + "/work/"
MONETA_TOOL_DIR = MONETA_BASE_DIR + "moneta/"
OUTPUT_DIR = MONETA_BASE_DIR + "moneta/output/"
CWD_HISTORY_PATH = OUTPUT_DIR + "cwd_history"
PIN_PATH  = "/pin/pin.sh"
#TOOL_PATH = MONETA_BASE_DIR + "setup/trace_tool.so"
TOOL_PATH = "/pin/source/tools/ManualExamples/obj-intel64/trace_tool.so"
WIDGET_DESC_PROP = {'description_width': '200px'}
WIDGET_LAYOUT = Layout(width='90%')

# Errors
ERROR_LABEL = f"{TextStyle.RED}{TextStyle.BOLD}Error:{TextStyle.END}"
WARNING_LABEL = f"{TextStyle.YELLOW}{TextStyle.BOLD}Warning:{TextStyle.END}"

NO_TAGS = (f"{ERROR_LABEL} {TextStyle.RED}No tags were traced\n\n"
           f"This means that either the start function does not exist, was inlined, or unable to be demangled"
           f"Try using the START_TRACE() call in your program")

## Vaex

### Dataframe Columns
INDEX = "index"
ADDRESS = "Address"
ACCESS = "Access"
TAG = "Tag"

### Axis Labels
INDEX_LABEL = "Access Number"
ADDRESS_LABEL = "Address Offset (Bytes)"

# Pintool Enumerations
COMP_W_MISS = 6
COMP_R_MISS = 5
WRITE_MISS = 4
READ_MISS = 3
WRITE_HIT = 2
READ_HIT = 1

# Tag file
LO_ADDR = "Low_Address"
HI_ADDR = "High_Address"
F_ACC = "First_Access"
L_ACC = "Last_Access"
TAG_NAME = "Tag_Name"

# Legend variables
LEGEND_MEM_ACCESS_TITLE = 'Accesses'
LEGEND_TAGS_TITLE = 'Tags'
LEGEND_CLICK_ZOOM = 'Click Zoom'
LEGEND_STATS_TITLE = 'Stats'

# Legend grid box
vdiv = HBox([
    VBox(layout=Layout(
        padding='0',
        border='1px solid black',
        width='0',
        height='50px', margin='0'))
    ], layout=Layout(justify_content='center'))
lvdiv = HBox([
    VBox(layout=Layout(
        padding='0',
        border='1px solid #cccbc8',
        width='0',
        height='50px', margin='0'))
            ], layout=Layout(justify_content='center'))
hdiv = VBox([
    HBox(layout=Layout(
        padding='0',
        border='1px solid black',
        width='100px',
        height='0'))
    ], layout=Layout(justify_content='center'))
lhdiv = VBox([
    HBox(layout=Layout(
        padding='0',
        border='1px solid #cccbc8',
        width='100px',
        height='0'))
            ], layout=Layout(justify_content='center'))
