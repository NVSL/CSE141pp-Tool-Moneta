from utils import collect_traces, delete_traces
import numpy as np
import vaex

import logging
log = logging.getLogger(__name__)

class Model():
    def __init__(self):
        log.info("Model __init__")
        self.curr_df = None
        self.curr_trace_name = str()
        self.output_traces = None
        self.trace_map = None

    def update_trace_list(self):
        self.output_traces, self.trace_map = collect_traces()
        return sorted(self.output_traces, key=str.casefold)

    def ready_next_trace(self):
        if self.curr_df:
            self.curr_df = None
            self.curr_trace_name = str()
            return False
        return True

    def load_trace(self, trace_name):
        log.info('Loading trace')
        trace_path, tag_path, meta_path = self.trace_map[trace_name]
        self.curr_trace_name = trace_name
        self.curr_df = vaex.open(trace_path)
        num_accs = self.curr_df.Address.count()
        self.curr_df['index'] = np.arange(0, num_accs)
        x_lim = [self.curr_df.index.min()[()], self.curr_df.index.max()[()]]
        y_lim = [self.curr_df.Address.min()[()], self.curr_df.Address.max()[()]]
        return x_lim, y_lim, self.curr_df


    def delete_traces(self, traces):
        delete_traces(map(lambda x: self.trace_map[x], traces))
        if self.curr_trace_name in traces:
            return False
        return True


