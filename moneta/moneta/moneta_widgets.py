from ipywidgets import VBox, HBox, Layout, Checkbox, SelectMultiple, Combobox, Label
from moneta.utils import (
    int_text_factory as int_field, 
    text_factory as text_field,
    button_factory as button,
    load_cwd_file,
    parse_exec_input
)
import moneta.settings as settings
import logging
import subprocess
log = logging.getLogger(__name__)

import ipyvuetify as v

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

        self.vh = v.Html(tag='style', children=[".v-input__slot .v-label{color: black!important}"])
        self.vh2 = v.Html(tag='style', children=[".vuetify-styles .v-messages {min-height: 0px!important}"])
        self.ft = v.Switch(v_model=False, label=settings.NORMAL_TRACE_DESC, inset=True, style_="color: black; background: white; margin-top: 0; padding-top: 10px; padding-left: 50px")
        self.ft.on_event("change", self.handle_full_trace)
        self.tm = v.Switch(v_model=False, label=settings.TRACK_NORMAL, inset=True, style_="color: black; background: white; margin-top: 0; padding-left: 50px")
        self.tm.on_event("change", self.handle_track_main)
        self.gt_in = VBox([self.cl, self.cb, self.ml, self.cwd, self.ex, self.to, self.ft, self.tm, self.vh, self.vh2], layout=Layout(width='100%'))
        self.gb = button(settings.GENERATE_DESC, color=settings.GENERATE_COLOR)
        self.lb = button(settings.LOAD_DESC, color=settings.LOAD_COLOR)
        self.db = button(settings.DELETE_DESC, color=settings.DELETE_COLOR)

        self.sw = SelectMultiple(
                options=[], value=[], description=settings.SELECT_MULTIPLE_DESC, layout=settings.WIDGET_LAYOUT, rows=10)
        self.tw = HBox([self.gt_in, self.sw], layout=Layout(justify_content='space-around'))
        self.bs = HBox([self.gb, self.lb, self.db])
        self.widgets = VBox([self.tw, self.bs], layout=Layout(justify_content='space-around'))

    def handle_full_trace(self, switch, _, new):
        switch.label = settings.FULL_TRACE_DESC if new else settings.NORMAL_TRACE_DESC

    def handle_track_main(self, switch, _, new):
        switch.label = settings.TRACK_MAIN if new else settings.TRACK_NORMAL
 
    def get_widget_values(self):
        e_file, e_args = parse_exec_input(self.ex.value)

        w_vals = {
            'c_lines': self.cl.value,
            'c_block': self.cb.value,
            'm_lines': self.ml.value,
            'cwd_path': self.cwd.value,
            'e_file': e_file,
            'e_args': e_args,
            'o_name': self.to.value,
            'is_full_trace': self.ft.v_model,
            'track_main': self.tm.v_model
        }
        return w_vals
