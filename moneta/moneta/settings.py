
from matplotlib.colors import ListedColormap
from ipywidgets import Layout, HBox, VBox, Layout
import numpy as np
import os

## File Chooser Settings
FC_WIDTH = "100%"
FC_SCROLLBOX_HEIGHT = "30vh"
FC_FILTER = ["*.hdf5"]
TRACE_FILE_END = ".hdf5"
TAG_FILE_END = ".tags"
META_FILE_END = ".meta"


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

PIN_PATH  = "/pin/pin.sh"
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
THREAD_ID = "ThreadID"

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
TAG_FILE_TAG_TYPE="Tag_Type"
TAG_FILE_THREAD_ID="Thread_ID"

# Legend variables
LEGEND_MEM_ACCESS_TITLE = 'Accesses'
LEGEND_TAGS_TITLE = 'Tags'
LEGEND_THREADS_TITLE = 'Threads'
LEGEND_STATS_TITLE = 'Stats'
LEGEND_MEASUREMENT_TITLE = 'Measurement'

# Stats Labels
STATS_HITS = "Hits"
STATS_COMP_MISS = "Comp. Misses"
STATS_CAP_MISS = "Cap. Misses"

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
