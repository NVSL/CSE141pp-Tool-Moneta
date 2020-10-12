from moneta.utils import collect_traces, delete_traces
from moneta.trace import Trace

import logging
log = logging.getLogger(__name__)

class Model():
    def __init__(self):
        log.info("__init__")
        self.curr_trace = None
        self.output_traces = None
        self.output_traces_full = None
        self.trace_map = None

    def update_trace_list(self):
        self.output_traces, self.output_traces_full, self.trace_map = collect_traces()
        return sorted(self.output_traces, key=str.casefold), sorted(self.output_traces_full, key=str.casefold)

    def ready_next_trace(self):
        if self.curr_trace is not None:
            self.curr_trace = None
            return False
        return True

    def load_trace(self, trace_name):
        trace_path, tag_path, meta_path = self.trace_map[trace_name]      
        self.curr_trace = Trace(trace_name, trace_path, tag_path, meta_path)
        return self.curr_trace.err_message


    def delete_traces(self, traces, lastChanged):
        if(lastChanged==1):
            delete_traces(map(lambda x: self.trace_map[x], traces))
        if(lastChanged==0):
            delete_traces(map(lambda x: self.trace_map["(Full) " + x], traces))
        
        if self.curr_trace is not None and self.curr_trace.name in traces:
            self.curr_trace = None
            return False
        return True
    