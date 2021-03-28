from ipywidgets import VBox, HBox, Layout, Checkbox, SelectMultiple, Combobox, Label
import logging
from cse142.utils import (
    int_text_factory as int_field, 
    text_factory as text_field,
    button_factory as button,
    parse_exec_input
)
import cse142.settings as settings
import ipyvuetify as v

log = logging.getLogger(__name__)

class CFGWidgets():
    def __init__(self):
        log.info("__init__")

        self.cwd = Combobox(
                placeholder=settings.CWD_PATH_DEF, options=load_cwd_file(settings.CFG_OUTPUT_DIR, settings.CWD_HISTORY_FILE_NAME),
                description=settings.CWD_PATH_DESC, style=settings.WIDGET_DESC_PROP, layout=settings.WIDGET_LAYOUT)
        
        self.ex = text_field(settings.EXEC_PATH_DEF, settings.EXEC_PATH_DESC)
        self.to = text_field(settings.TRACE_NAME_DEF, settings.TRACE_NAME_DESC)

        self.vh = v.Html(tag='style', children=[".v-input__slot .v-label{color: black!important}"])

        self.gt_in = VBox([
            self.cwd, 
            self.ex, 
            self.to, 
            self.vh
            ], layout=Layout(width='100%'))

        self.gb = button(settings.GENERATE_DESC, color=settings.GENERATE_COLOR)
        self.lb = button(settings.LOAD_DESC, color=settings.LOAD_COLOR)
        self.db = button(settings.DELETE_DESC, color=settings.DELETE_COLOR)
        self.bs = HBox([self.gb, self.lb, self.db])

        self.sw = SelectMultiple(
                options=[], value=[], description=settings.SELECT_MULTIPLE_DESC, layout=settings.WIDGET_LAYOUT, rows=10)

        self.tw = HBox([self.gt_in, self.sw], layout = Layout(justify_content="space-around"))
        self.widgets = VBox([self.tw, self.bs], layout=Layout(justify_content="space-around"))

    def get_widget_values(self):
        e_file, e_args = parse_exec_input(self.ex.value)

        w_vals = {
            'cwd_path': self.cwd.value,
            'e_file': e_file,
            'e_args': e_args,
            'o_name': self.to.value,
        }
        return w_vals
