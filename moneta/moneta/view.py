from IPython.display import clear_output, display
from moneta.settings import CUSTOM_CMAP, MONETA_BASE_DIR, INDEX_LABEL, ADDRESS_LABEL, INDEX, ADDRESS, HISTORY_MAX, CWD_HISTORY_PATH
from moneta.utils import (
    generate_trace, 
    delete_traces, 
    update_cwd_file,
    update_legend_view_stats
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

        #added to resolve first one not being correct error 
        self.m_widget.sw.observe(self.on_value_change, names='value')
        self.m_widget.sw2.observe(self.on_value_change2, names='value')
        

    def init_widgets(self):
        log.info("Initializing widgets")
        self.m_widget = MonetaWidgets()
        self.m_widget.gb.on_click(self.handle_generate_trace)
        self.m_widget.lb.on_click(self.handle_load_trace)
        self.m_widget.db.on_click(self.handle_delete_trace)
        self.lastChanged = -1
        self.update_select_widget()
        
        self.w_1 = []
        self.w_2 = []
        self.selectors = [self.m_widget.sw, self.m_widget.sw2]
        
        display(self.m_widget.widgets)

    def update_select_widget(self):
        self.m_widget.sw.options,self.m_widget.sw2.options = self.model.update_trace_list()
        self.m_widget.sw.value = []
        self.m_widget.sw2.value = []
       

    def on_value_change(self, change):
        self.m_widget.sw2.value = ()
        self.m_widget.sw.value = change['new']
        if(not change['new']):
            self.lastChanged=-1
        else:
            self.lastChanged = 1

    def on_value_change2(self, change):
        self.m_widget.sw.value = ()
        self.m_widget.sw2.value = change['new']
        if(not change['new']):
            self.lastChanged=-1
        else:
            self.lastChanged = 0

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


        if (self.m_widget.sw.value is None or len(self.m_widget.sw.value) == 0) and (self.m_widget.sw2.value is None or len(self.m_widget.sw2.value) == 0):
            print("To load a trace, select a trace")
            return
        elif len(self.m_widget.sw.value) > 1 or len(self.m_widget.sw2.value) > 1:
            print("To load a trace, select a single trace")
            return
        elif(len(self.m_widget.sw.value)!=0 and len(self.m_widget.sw2.value)!=0):
            print("To load a trace, select a single trace from Tagged or Full Traces")

        if(self.lastChanged==1):
            #curr_trace, err_message = self.model.load_trace(self.m_widget.sw.value[0])
            err_message = self.model.load_trace(self.m_widget.sw.value[0])

        elif(self.lastChanged==0):
            #curr_trace, err_message = self.model.load_trace("(Full) " + self.m_widget.sw2.value[0])
            err_message = self.model.load_trace("(Full) " + self.m_widget.sw2.value[0])

        else:
            log.debug("No trace chosen to load")
            return
          
        #err_message = self.model.load_trace(self.m_widget.sw.value[0])
        if err_message is not None:
            print(err_message)
            return

        log.info(self.lastChanged)
        self.model.create_plot()
        if self.model.plot is None:
            print("Couldn't load plot")
            return

        self.model.plot.show()

        update_legend_view_stats(self.model.legend.stats, self.model.plot, self.model.legend.get_select_string(), True)

        pass
    
    def handle_delete_trace(self, _):
        log.info("Delete Trace clicked")

        if(self.lastChanged==1):
            log.info("Deleting tagged trace")
            if (not self.model.delete_traces(self.m_widget.sw.value, 1)):
                clear_output(wait=True)
                log.info("Refreshing")
                display(self.m_widget.widgets)
            self.update_select_widget()
            pass
        elif (self.lastChanged==0):
            log.info("Deleting full trace")
            if (not self.model.delete_traces(self.m_widget.sw2.value, 0)):
                clear_output(wait=True)
                log.info("Refreshing")
                display(self.m_widget.widgets)
            self.update_select_widget()
            pass
        else:
            log.debug("No trace chosen to delete")
