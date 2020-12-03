from moneta.settings import CUSTOM_CMAP, INDEX_LABEL, ADDRESS_LABEL, INDEX, ADDRESS
from moneta.utils import collect_traces, delete_traces 
from moneta.legend.legend import Legend
from moneta.trace import Trace

import logging
log = logging.getLogger(__name__)

class Model():
    def __init__(self):
        log.info("__init__")
        self.output_traces = None
        self.trace_map = None

        self.curr_trace = None
        self.legend = None
        self.plot = None

    def update_trace_list(self):
        self.output_traces, self.trace_map = collect_traces()
        return sorted(self.output_traces, key=str.casefold)

    def clear_trace_state(self):
        self.curr_trace = None
        self.legend = None
        self.plot = None

    def ready_next_trace(self):
        if self.curr_trace is not None:
            self.clear_trace_state()
            return False
        return True

    def load_trace(self, trace_name):
        trace_path, tag_path, meta_path = self.trace_map[trace_name]      
        self.curr_trace = Trace(trace_name, trace_path, tag_path, meta_path)
        return self.curr_trace.err_message

    def cache_size(self):
        return self.curr_trace.cache_lines*self.curr_trace.cache_block

    def plot_title(self):
        return (
                f"{self.curr_trace.name} - "
                f"Cache: {self.curr_trace.cache_block}-byte block, "
                f"{self.curr_trace.cache_lines} Lines "
            )

    def create_plot(self):
        self.legend = Legend(self)
        self.plot = self.curr_trace.df.plot_widget(
                    self.curr_trace.df[INDEX], self.curr_trace.df[ADDRESS], 
                    what='max(Access)', colormap=CUSTOM_CMAP, 
                    selection=[True], limits=[self.curr_trace.x_lim, self.curr_trace.y_lim],
                    backend='moneta_backend', type='vaextended', model=self,
                    x_col=INDEX, y_col=ADDRESS, x_label=INDEX_LABEL, y_label=ADDRESS_LABEL, 
                    update_stats=self.legend.stats.update,
                    show=False
                 )
        self.legend.init_clickzoom()

    def delete_traces(self, traces):
        delete_traces(map(lambda x: self.trace_map[x], traces))
        
        if self.curr_trace is not None and self.curr_trace.name in traces:
            self.clear_trace_state()
            return False
        return True
    
