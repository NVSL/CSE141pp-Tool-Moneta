from moneta.settings import CUSTOM_CMAP, INDEX_LABEL, ADDRESS_LABEL, INDEX, ADDRESS, TRACE_FILE_END, META_FILE_END, TAG_FILE_END
from moneta.legend.legend import Legend
from moneta.trace import Trace
import vaex.jupyter.plot
vaex.jupyter.plot.backends['moneta_backend'] = ("moneta.vaextended.bqplot", "BqplotBackend")

class Moneta():
    def __init__(self):
        self.output_traces = None
        self.trace_map = dict()

        self.curr_trace = None
        self.legend = None
        self.plot = None

    def load_trace(self, path, trace_name):
        raw_trace_name = trace_name.replace(TRACE_FILE_END, '')
        trace_path = f'{path}/{raw_trace_name}{TRACE_FILE_END}'
        tag_path = f'{path}/{raw_trace_name}{TAG_FILE_END}'
        meta_path = f'{path}/{raw_trace_name}{META_FILE_END}'

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
            self.curr_trace.df[INDEX],
            self.curr_trace.df[ADDRESS], 
            what='max(Access)',
            colormap=CUSTOM_CMAP, 
            selection=[True],
            limits=self.curr_trace.get_initial_zoom(),
            backend='moneta_backend',
            #backend='simple_backend',
            type='vaextended',
            model=self,
            x_col=INDEX,
            y_col=ADDRESS,
            x_label=INDEX_LABEL,
            y_label=ADDRESS_LABEL, 
            update_stats=self.legend.stats.update,
            show=False
        )

