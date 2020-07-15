from ipywidgets import Text, Button, VBox, HBox, Layout, Checkbox, IntText, Label, Dropdown, SelectMultiple, ColorPicker
import os
import re
import sys
import vaex
import vaex.jupyter
#import vaex.jupyter.plot
import argparse
import subprocess
import numpy as np
from matplotlib.colors import ListedColormap
from IPython.display import clear_output

PIN_DIR  = "/setup/pintool/pin.sh"
TOOL_DIR = "/setup/converter/trace_tool.so"
OUTPUT_DIR = "/setup/converter/outfiles/"

# Constants
WIDGET_DESC_PROP = {'description_width': '150px'}
WIDGET_LAYOUT = Layout(width='90%')
BUTTON_LAYOUT = Layout(margin='15px 15px 0 15px',
                       height='40px', width='90%', border='1px solid black')
BUTTON_STYLE = {'button_color': 'lightgray'}

DEFAULT_TRACE_DROP = 'Select a trace to load'


import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser(description='Display and control UI.')
parser.add_argument('-r', action='store_true',
                    help='When enabled, refresh to minimize cell output')
parser.add_argument('-log', action='store_true',
                    help='When enabled, Show debug/info logging')
args,unknown = parser.parse_known_args()

if not args.log:
  logging.disable(logging.CRITICAL) # To disable logger


def refresh():
  """Clears Jupyter notebook's cell output and displays inputs again"""
  clear_output(wait=True)
  logging.info("Refreshing")
  display(all_inputs)


#Enumerations
COMP_W_MISS = 6
COMP_R_MISS = 5
WRITE_MISS = 4
READ_MISS = 3
WRITE_HIT = 2
READ_HIT = 1



# Globals
trace_list = []
trace_map = dict()
trace_metadata = dict()
all_inputs = VBox()
currentSelection = [1,1,1,1,1,1]


df = 0
tag_map = 0
curr_trace = ""
COLORPALETTE_EDITABLE = True

def button_factory(desc, color='lightgray'):
  return Button(
          description=desc,
          button_style='',
          layout = BUTTON_LAYOUT,
          style = {'button_color': color}
         )


def input_int_factory(value, description):
  return IntText(
          value=value,
          description=description,
          style=WIDGET_DESC_PROP,
          layout=WIDGET_LAYOUT
         )


def input_text_factory(placeholder, description):
  return Text(
          value='',
          placeholder=placeholder,
          description=description,
          style=WIDGET_DESC_PROP,
          layout=WIDGET_LAYOUT
         )



