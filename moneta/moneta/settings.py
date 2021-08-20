
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

# Enviroment Variables
COLOR_VIEW = 'COLOR_VIEW'
C_VIEW_OPTIONS = ['All', 'AccessType', 'TAG', 'THREAD', 'Custom2', 'Custom4', 'Custom8']

# Colormap
# newc = np.ones((11, 4)) # why 11 I dont know eithier
# newc[1] = [0, 0, 1, 1] # read_hits - 1, .125
# newc[2] = [0, 153/255, 204/255, 1] # write_hits - 2, .25
# newc[3] = [0.047, 1, 0, 1] # cache_size
# newc[4] = [1, .5, 0, 1] # read_misses - 3, .375
# newc[5] = [1, 0, 0, 1] # write_misses - 4, .5
# newc[6] = [0.5, 0.3, 0.1, 1] # compulsory read misses - 5, .625
# newc[8] = [0.745, 0.309, 0.235, 1] # compulsory write misses - 6, .75
# CUSTOM_CMAP = ListedColormap(newc)


newc = np.ones((11, 4)) # why 11 I dont know eithier
newc[1] = [0, 0, 0, 1] # layer 0 black
newc[2] = [0, 153/255, 204/255, 1] # layer 1 light blue
newc[3] = [0.047, 1, 0, 1] # cache_size
newc[4] = [1, .5, 0, 1] # layer 2  red
newc[5] = [1, 0, 0, 1] # layer 3
newc[6] = [0.5, 0.3, 0.1, 1] # layer 4
newc[8] = [0.745, 0.309, 0.235, 1] # layer 5
CUSTOM_CMAP = ListedColormap(newc)





# Colors of top level choices. This is handled differenly since these colors
# control many access types.
# [r g b a accesstype1 accesstype2 ...]
# READS_CLR = [187/255, 0/255, 255/255, 1, 1, 4, 6]
# WRITES_CLR = [0, 255/255, 255/255, 1, 2, 5, 8]
# HIT_CLR = [215/255, 230/255, 10/255, 1, 1, 2] 
# MISS_CAP_CLR = [0/255, 0/255, 0/255, 1, 4, 5]
# MISS_COM_CLR = [0/255, 0/255, 0/255, 1, 6, 8]


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

# Access Type Identifiers
# Not part of pin tool but still used to identify accesses 
TOP_COM_MISS = 20
TOP_CAP_MISS = 21
TOP_HIT = 22
TOP_WRITE = 23
TOP_READ = 24
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
