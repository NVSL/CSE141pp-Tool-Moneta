from ipywidgets import VBox, HBox, Layout, Checkbox, SelectMultiple, Combobox
from utils import int_text_factory as int_field
from utils import text_factory as text_field
from utils import button_factory as button
from utils import load_cwd_file, parse_cwd, parse_exec_input
import settings
import logging
import subprocess
import os
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
        self.gt_in = VBox([self.cl, self.cb, self.ml, self.cwd, self.ex, self.to, self.ft], layout=Layout(width='100%'))
        self.gb = button(settings.GENERATE_DESC, color=settings.GENERATE_COLOR)
        self.lb = button(settings.LOAD_DESC, color=settings.LOAD_COLOR)
        self.db = button(settings.DELETE_DESC, color=settings.DELETE_COLOR)

        self.sw = SelectMultiple(
                options=[], value=[], description=settings.SELECT_MULTIPLE_DESC, layout=settings.WIDGET_LAYOUT, rows=10)
        self.tw = HBox([self.gt_in, self.sw], layout=Layout(justify_content='space-around'))
        self.bs = HBox([self.gb, self.lb, self.db])
        self.widgets = VBox([self.tw, self.bs], layout=Layout(justify_content='space-around'))

    def get_widget_values(self):
        e_file, e_args = parse_exec_input(self.ex.value)

        w_vals = {
            'c_lines': self.cl.value,
            'c_block': self.cb.value,
            'm_lines': self.ml.value,
            'cwd_path': os.path.expanduser(parse_cwd(self.cwd.value)),
            'e_file': e_file,
            'e_args': e_args,
            'o_name': self.to.value,
            'is_full_trace': self.ft.value
        }
        return w_vals