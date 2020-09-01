from ipywidgets import VBox, HBox, Layout, Checkbox, SelectMultiple, Combobox, Label
from utils import int_text_factory as int_field
from utils import text_factory as text_field
from utils import button_factory as button
from utils import load_cwd_file, parse_cwd, parse_exec_input
import settings
import logging
import subprocess
import os
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
        self.ft = v.Switch(label=settings.NORMAL_TRACE_DESC, inset=True, style_="color: black; background: white; margin-top: 0; padding-top: 10px; padding-left: 50px")
        self.ft.on_event("change", self.switch_handler)
        self.gt_in = VBox([self.cl, self.cb, self.ml, self.cwd, self.ex, self.to, self.ft, self.vh], layout=Layout(width='100%'))
        self.gb = button(settings.GENERATE_DESC, color=settings.GENERATE_COLOR)
        self.lb = button(settings.LOAD_DESC, color=settings.LOAD_COLOR)
        self.db = button(settings.DELETE_DESC, color=settings.DELETE_COLOR)

        self.sw = SelectMultiple(
                options=[], value=[], description=settings.SELECT_MULTIPLE_DESC, layout=settings.WIDGET_LAYOUT, rows=10)
        self.tw = HBox([self.gt_in, self.sw], layout=Layout(justify_content='space-around'))
        self.bs = HBox([self.gb, self.lb, self.db])
        self.widgets = VBox([self.tw, self.bs], layout=Layout(justify_content='space-around'))



        self.total_stat_title = Label(
                           value='Total Stats:',
                           layout=settings.WIDGET_LAYOUT
                           )
        self.total_hits = Label(layout=settings.WIDGET_LAYOUT)
        self.total_cap_misses = Label(layout=settings.WIDGET_LAYOUT)
        self.total_comp_misses = Label(layout=settings.WIDGET_LAYOUT)
        self.total_stats = VBox(
                           [self.total_stat_title, self.total_hits, self.total_cap_misses, self.total_comp_misses],
                           layout=Layout(width='500px')
                           )

        self.curr_stat_title = Label(
                           value='Current View Stats:',
                           layout=settings.WIDGET_LAYOUT
                           )
        self.curr_hits = Label(layout=settings.WIDGET_LAYOUT)
        self.curr_cap_misses = Label(layout=settings.WIDGET_LAYOUT)
        self.curr_comp_misses = Label(layout=settings.WIDGET_LAYOUT)
        self.curr_stats = VBox(
                          [self.curr_stat_title, self.curr_hits, self.curr_cap_misses, self.curr_comp_misses],
                          layout=Layout(width='500px')
                          )

        self.stats = HBox([self.total_stats, self.curr_stats])

    def switch_handler(self, switch, *_):
        switch.value = not switch.value
        switch.label = settings.FULL_TRACE_DESC if switch.value else settings.NORMAL_TRACE_DESC
        
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
