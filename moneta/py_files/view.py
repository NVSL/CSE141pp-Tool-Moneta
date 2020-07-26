from IPython.display import clear_output, display
from settings import CUSTOM_CMAP, MONETA_BASE_DIR
from utils import generate_trace, delete_traces
import moneta_widgets
import sys
sys.path.append(MONETA_BASE_DIR + '.setup/')
import vaex
import vaex_extended
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot', 'BqplotBackend')

import logging
log = logging.getLogger(__name__)

class View():
    def __init__(self, model):
        log.info('View __init__')
        self.model = model
        self.init_widgets()

    def init_widgets(self):
        log.info("Initializing widgets")
        self.m_widget = moneta_widgets.MonetaWidgets()
        self.m_widget.gb.on_click(self.handle_generate_trace)
        self.m_widget.lb.on_click(self.handle_load_trace)
        self.m_widget.db.on_click(self.handle_delete_trace)
        self.update_select_widget()
        display(self.m_widget.widgets)

    def update_select_widget(self):
        self.m_widget.sw.options = self.model.update_trace_list()
        self.m_widget.sw.value = []

    def handle_generate_trace(self, _):
        log.info('Generate Trace clicked')
        w_vals = [self.m_widget.cl.value,
                self.m_widget.cb.value,
                self.m_widget.ml.value,
                self.m_widget.ex.value,
                self.m_widget.to.value,
                self.m_widget.ft.value]
        if generate_trace(*w_vals):
            self.update_select_widget()

    def handle_load_trace(self, _):
        log.info('Load Trace clicked')
        if (not self.model.ready_next_trace()):
            clear_output(wait=True)
            log.info('Refreshing')
            display(self.m_widget.widgets)

        x_lim, y_lim, df = self.model.load_trace(self.m_widget.sw.value[0])
        plot = df.plot_widget(df.index, df.Address, what='max(Access)',
                 colormap = CUSTOM_CMAP, selection=[True], limits = [x_lim, y_lim],
                 backend='bqplot_v2', tool_select=True, type='custom_plot1')
        pass
    
    def handle_delete_trace(self, _):
        log.info('Delete Trace clicked')
        if (not self.model.delete_traces(self.m_widget.sw.value)):
            clear_output(wait=True)
            log.info('Refreshing')
            display(self.m_widget.widgets)
        self.update_select_widget()
        pass


