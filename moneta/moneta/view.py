from IPython.display import clear_output, display
from settings import CUSTOM_CMAP, MONETA_BASE_DIR, INDEX_LABEL, ADDRESS_LABEL, HISTORY_MAX, CWD_HISTORY_PATH
from utils import generate_trace, delete_traces, update_cwd_file, parse_cwd
from moneta_widgets import MonetaWidgets
from legend import Legend
import vaex
import vaex.jupyter.plot
vaex.jupyter.plot.backends['bqplot_v2'] = ("vaextended.bqplot", "BqplotBackend")

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
        self.update_select_widget()
        self.update_select_widget_full()
        
        self.w_1 = []
        self.w_2 = []
        self.selectors = [self.m_widget.sw, self.m_widget.sw2]
        self.lastChanged = -1
        
        display(self.m_widget.widgets)

    def update_select_widget(self):
        self.m_widget.sw.options = self.model.update_trace_list()
        self.m_widget.sw.value = []

    #added for second select_widget (full)
    def update_select_widget_full(self):
        self.m_widget.sw2.options = self.model.update_trace_list_full()
        self.m_widget.sw2.value = []

    def on_value_change(self, change):
        self.m_widget.sw2.value = ()
        self.m_widget.sw.value = change['new']
        self.lastChanged = 1

    def on_value_change2(self, change):
        self.m_widget.sw.value = ()
        self.m_widget.sw2.value = change['new']
        self.lastChanged = 0

    def update_cwd_widget(self, cwd_path):
        cwd_path = parse_cwd(cwd_path)
        if not cwd_path in (".", "./") and not cwd_path in self.m_widget.cwd.options:
            self.m_widget.cwd.options = [cwd_path, *self.m_widget.cwd.options][0:HISTORY_MAX]
            update_cwd_file(self.m_widget.cwd.options)
            log.debug("New History: {}".format(self.m_widget.cwd.options))
            
        
    def handle_generate_trace(self, _):
        log.info("Generate Trace clicked")
        self.m_widget.sw.observe(self.on_value_change, names='value')
        self.m_widget.sw2.observe(self.on_value_change2, names='value')

        w_vals = [
            self.m_widget.cl.value,
            self.m_widget.cb.value,
            self.m_widget.ml.value,
            self.m_widget.cwd.value,
            self.m_widget.ex.value,
            self.m_widget.to.value,
            self.m_widget.ft.value
        ]
        
        if generate_trace(*w_vals):
            self.update_cwd_widget(self.m_widget.cwd.value)
            self.update_select_widget()
            self.update_select_widget_full()

    def handle_load_trace(self, _):
        log.info("Load Trace clicked")
        self.m_widget.sw.observe(self.on_value_change, names='value')
        self.m_widget.sw2.observe(self.on_value_change2, names='value')
        if (not self.model.ready_next_trace()):
            clear_output(wait=True)
            log.info("Refreshing")
            display(self.m_widget.widgets)

        log.info(self.lastChanged)

        if(self.lastChanged==1):
            curr_trace, err_message = self.model.load_trace(self.m_widget.sw.value[0])
            log.info("in tag conditional")
            if err_message is not None:
                print(err_message)
                return
        elif(self.lastChanged==0):
            curr_trace, err_message = self.model.load_trace_full(self.m_widget.sw2.value[0])
            log.info("in full conditional")
            if err_message is not None:
                print(err_message)
                return
        else:
            print("no trace chosen")

        log.info(self.lastChanged)
        log.info("reach the end of conditionals")
        df = curr_trace.df
        x_lim = curr_trace.x_lim
        y_lim = curr_trace.y_lim
        cache_size = curr_trace.cache_lines*curr_trace.cache_block
        tags = curr_trace.tags
        legend = Legend(tags, df)
        plot = df.plot_widget(df[INDEX_LABEL], df[ADDRESS_LABEL], what='max(Access)',
                 colormap = CUSTOM_CMAP, selection=[True], limits = [x_lim, y_lim],
                 backend='bqplot_v2', type='custom_plot1', legend=legend.widgets,
                 x_label=INDEX_LABEL, y_label=ADDRESS_LABEL, cache_size=cache_size)

        legend.set_zoom_sel_handler(plot.backend.zoom_sel)
        legend.set_plot(plot)
        pass
    
    def handle_delete_trace(self, _):
        log.info("Delete Trace clicked")
        self.m_widget.sw.observe(self.on_value_change, names='value')
        self.m_widget.sw2.observe(self.on_value_change2, names='value')
        print(self.lastChanged)
        tag_or_full = self.lastChanged
        #initialized as -1
        if(tag_or_full == 1):
            print("tagged trace chosen")
        #1 means tag
        elif (tag_or_full == 0): 
            print("full trace chosen")
        else:
        #0 means full
            print("No trace chosen!")

        #This is the functionality to actually delete the trace, 
        # it's commented out to make sure we get the right verdict
        #from our obseerved_function
        #           vvvvvvvvvv
        if(self.lastChanged==1):
            print("deleting tag")
            if (not self.model.delete_traces(self.m_widget.sw.value)):
                clear_output(wait=True)
                log.info("Refreshing")
                display(self.m_widget.widgets)
            self.update_select_widget()
            pass
        elif (self.lastChanged==0):
            print("deleting full")
            if (not self.model.delete_traces_full(self.m_widget.sw2.value)):
                clear_output(wait=True)
                log.info("Refreshing")
                display(self.m_widget.widgets)
            self.update_select_widget_full()
            pass
        else:
            print("none to delete")
