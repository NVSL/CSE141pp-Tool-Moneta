from ipywidgets import VBox, HBox, Layout, Checkbox, SelectMultiple, Combobox
from utils import int_text_factory as int_field
from utils import text_factory as text_field
from utils import button_factory as button
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

        cwd_options = self.load_cwd_history()

        self.cwd = Combobox(
                placeholder=settings.CWD_PATH_DEF, options=cwd_options,description=settings.CWD_PATH_DESC,
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

        
    def load_cwd_history(self):
        try:
            with open(settings.CWD_HISTORY_PATH, "w+") as history:
                cwd_history = history.read().split()
                logging.debug("Working Directory History: {}".format(cwd_history))
                return cwd_history
        except Exception as e: 
            # Allows tool to still work, just no history, if there is a problem with the file
            log.debug("History file error: \n{}".format(e))
            return []