from IPython.display import clear_output, display
from moneta.settings import HISTORY_MAX 
from moneta.utils import (
    generate_trace, 
    delete_traces, 
    update_cwd_file
)
from moneta.moneta_widgets import MonetaWidgets
from moneta.legend.legend import Legend
import vaex
import vaex.jupyter.plot
vaex.jupyter.plot.backends['moneta_backend'] = ("vaextended.bqplot", "BqplotBackend")

import logging
log = logging.getLogger(__name__)

class View():
    def __init__(self, model):
        log.info("__init__")
        self.model = model
        self.init_widgets()

    def init_widgets(self):
        log.info("Initializing widgets")
        self.m_widget = MonetaWidgets()
        self.m_widget.gb.on_click(self.handle_generate_trace)
        self.m_widget.lb.on_click(self.handle_load_trace)
        self.m_widget.db.on_click(self.handle_delete_trace)
        self.update_select_widget()
        
        display(self.m_widget.widgets)

    def update_select_widget(self):
        self.m_widget.sw.options = self.model.update_trace_list()
        self.m_widget.sw.value = []
       
    def update_cwd_widget(self, cwd_path):
        if not cwd_path in (".", "./") and not cwd_path in self.m_widget.cwd.options:
            self.m_widget.cwd.options = [cwd_path, *self.m_widget.cwd.options][0:HISTORY_MAX]
            update_cwd_file(self.m_widget.cwd.options)
            log.debug(f"New History: {self.m_widget.cwd.options}")
            
    def handle_generate_trace(self, _):
        log.info("Generate Trace clicked")
        
        w_vals = self.m_widget.get_widget_values()

        if generate_trace(w_vals):
            self.update_cwd_widget(w_vals['display_path'])
            self.update_select_widget()

    def handle_load_trace(self, _):
        log.info("Load Trace clicked")

        self.model.ready_next_trace()
        clear_output(wait=True)
        log.info("Refreshing")
        display(self.m_widget.widgets)


        if self.m_widget.sw.value is None or len(self.m_widget.sw.value) == 0:
            print("To load a trace, select a trace")
            return
        elif len(self.m_widget.sw.value) > 1:
            print("To load a trace, select a single trace")
            return
        err_message = self.model.load_trace(self.m_widget.sw.value[0])

        if err_message is not None:
            print(err_message)
            return

        self.model.create_plot()

        if self.model.plot is None:
            print("Couldn't load plot")
            return

        self.model.plot.show()
        self.model.legend.stats.update(init=True)
    
    def handle_delete_trace(self, _):
        log.info("Delete Trace clicked")
        if (not self.model.delete_traces(self.m_widget.sw.value)):
            clear_output(wait=True)
            log.info("Refreshing")
            display(self.m_widget.widgets)
        self.update_select_widget()
        pass
