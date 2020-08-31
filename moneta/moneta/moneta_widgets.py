from ipywidgets import VBox, HBox, Layout, Checkbox, SelectMultiple, Combobox, HTML, Box
from utils import int_text_factory as int_field
from utils import text_factory as text_field
from utils import button_factory as button
from utils import load_cwd_file
import settings
import logging
import subprocess
log = logging.getLogger(__name__)

class MonetaWidgets():
    def __init__(self):
        log.info("__init__")
        self.cl = int_field(settings.CACHE_LINES_VAL, settings.CACHE_LINES_DESC)
        self.cb = int_field(settings.CACHE_BLOCK_VAL, settings.CACHE_BLOCK_DESC)
        self.ml = int_field(settings.OUTPUT_LINES_VAL, settings.OUTPUT_LINES_DESC)
        
        self.cwd = Combobox(
                placeholder=settings.CWD_PATH_DEF, options=load_cwd_file(),description=settings.CWD_PATH_DESC,
                style=settings.WIDGET_DESC_PROP, layout=settings.WIDGET_LAYOUT)
        
        self.ex = text_field(settings.EXEC_PATH_DEF, settings.EXEC_PATH_DESC)
        self.to = text_field(settings.TRACE_NAME_DEF, settings.TRACE_NAME_DESC)

        self.ft = Checkbox(description=settings.FULL_TRACE_DESC, value=False, indent=False)
        #self.gt_in = VBox([self.cl, self.cb, self.ml, self.cwd, self.ex, self.to, self.ft], layout=Layout(width='100%'))
        self.gt_in = VBox([self.cl, self.cb, self.ml, self.cwd, self.ex, self.to, self.ft], layout=Layout(width='50%'))
        self.gb = button(settings.GENERATE_DESC, color=settings.GENERATE_COLOR)
        self.lb = button(settings.LOAD_DESC, color=settings.LOAD_COLOR)
        self.db = button(settings.DELETE_DESC, color=settings.DELETE_COLOR)

        self.sw = SelectMultiple(
                options=[], value=[],layout=settings.TW_LAYOUT, rows=10)
  #added      
        self.sw2 = SelectMultiple (
                options=[], value=[],layout=settings.TW_LAYOUT, rows=10)
        self.tt = HTML( value="<center>Tagged Trace</center>", layout=settings.TW_LAYOUT)
        self.tf =  HTML( value="<center>Full Trace</center>", layout=settings.TW_LAYOUT)
        #box for titles
        self.tBox = Box(children=[self.tt, self.tf], layout=settings.TW_BOX_LAYOUT)
        self.swBox = Box(children=[self.sw, self.sw2], layout=settings.TW_BOX_LAYOUT)
        self.traces = VBox([self.tBox, self.swBox], layout = Layout(flex='1 1 0%', width = 'auto'))
        #box for widgets
        #self.tw = HBox([self.gt_in, self.traces])
        #self.tw = HBox([self.gt_in, self.traces], layout=Layout(justify_content='space-around'))
        self.tw = HBox([self.gt_in, self.traces], layout = Layout(flex='1 1 0%'))
        self.bs = HBox([self.gb, self.lb, self.db])
        #self.widgets = VBox([self.tw, self.bs], layout=Layout(justify_content='space-around'))
        self.widgets = VBox([self.tw, self.bs], layout=Layout(flex='1 1 0%'))

