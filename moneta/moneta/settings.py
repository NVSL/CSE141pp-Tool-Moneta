
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

# layer options
C_VIEW_OPTIONS = ['None', 'AccessType', 'TAG', 'THREAD', 'Custom']


# Colormap can be extended to any size, however the first and last 2 indexes must be white
newc = np.ones((12, 4))
# 0 index must be white
newc[1] = [95/255, 95/255, 95/255, 1] # layer 1 grey
newc[2] = [0, 153/255, 204/255, 1] # baby blue
newc[3] = [128/255, 76/255, 26/255, 1] # brown 
newc[4] = [255/255, 128/255, 0/255, 1] # orange
newc[5] = [9/255, 113/255, 63/255, 1] #  2 green
newc[6] = [1, 0, 0, 1] # red
newc[7] = [187/255, 0/255, 255/255, 1] # magenta
newc[8] = [0, 255/255, 255/255, 1] # cyan
newc[9] = [215/255, 230/255, 10/255, 1] # yellow
newc[10] = [0/255, 255/255, 0/255, 1] # cache green
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
LAYER = "Layer"

### Axis Labels
INDEX_LABEL = "Access Number"
ADDRESS_LABEL = "Address Offset (Bytes)"

# Access Type Identifiers
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
LEGEND_MEM_ACCESS_TITLE = 'Accesses Layers'
LEGEND_TAGS_TITLE = 'Tags'
LEGEND_THREADS_TITLE = 'Threads'
LEGEND_STATS_TITLE = 'Stats'
LEGEND_MEASUREMENT_TITLE = 'Cache Measurement'

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
        width='120px',
        height='0'))
    ], layout=Layout(justify_content='center'))
Whdiv = VBox([
    HBox(layout=Layout(
        padding='0',
        border='1px solid black',
        width='180px',
        height='0'))
    ], layout=Layout(justify_content='center'))
lhdiv = VBox([
    HBox(layout=Layout(
        padding='0',
        border='1px solid #cccbc8',
        width='120px',
        height='0'))
            ], layout=Layout(justify_content='center'))
