from IPython.display import clear_output, display
from moneta.settings import CUSTOM_CMAP, MONETA_BASE_DIR, INDEX_LABEL, ADDRESS_LABEL, HISTORY_MAX, CWD_HISTORY_PATH
from moneta.utils import (
    generate_trace, 
    delete_traces, 
    update_cwd_file, 
    get_curr_stats,
    stats_hit_string,
    stats_cap_miss_string,
    stats_comp_miss_string
)
from moneta.moneta_widgets import MonetaWidgets
from moneta.legend import Legend
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
            log.debug("New History: {}".format(self.m_widget.cwd.options))
            
        
    def update_stats_widget(self, plot, is_load_trace):
        total_count, hit_count, cap_miss_count, comp_miss_count = get_curr_stats(plot)

        if(is_load_trace):
            self.m_widget.total_hits.value = stats_hit_string(hit_count, total_count)
            self.m_widget.total_cap_misses.value = stats_cap_miss_string(cap_miss_count, total_count)
            self.m_widget.total_comp_misses.value = stats_comp_miss_string(comp_miss_count, total_count)

        self.m_widget.curr_hits.value = stats_hit_string(hit_count, total_count)
        self.m_widget.curr_cap_misses.value = stats_cap_miss_string(cap_miss_count, total_count)
        self.m_widget.curr_comp_misses.value = stats_comp_miss_string(comp_miss_count, total_count)


    def handle_generate_trace(self, _):
        log.info("Generate Trace clicked")
        
        w_vals = self.m_widget.get_widget_values()

        if generate_trace(w_vals):
            self.update_cwd_widget(w_vals['display_path'])
            self.update_select_widget()

    def handle_load_trace(self, _):
        log.info("Load Trace clicked")
        if (not self.model.ready_next_trace()):
            clear_output(wait=True)
            log.info("Refreshing")
            display(self.m_widget.widgets)

        curr_trace, err_message = self.model.load_trace(self.m_widget.sw.value[0])
        if err_message is not None:
            print(err_message)
            return

        df = curr_trace.df
        x_lim = curr_trace.x_lim
        y_lim = curr_trace.y_lim
        cache_size = curr_trace.cache_lines*curr_trace.cache_block
        tags = curr_trace.tags
        legend = Legend(tags, df)
        plot = df.plot_widget(df[INDEX_LABEL], df[ADDRESS_LABEL], what='max(Access)',
                 colormap = CUSTOM_CMAP, selection=[True], limits = [x_lim, y_lim],
                 backend='moneta_backend', type='vaextended', legend=legend,
                 default_title=curr_trace.name, x_label=INDEX_LABEL, y_label=ADDRESS_LABEL, cache_size=cache_size,
                 update_stats = lambda *ignore: self.update_stats_widget(plot, False)
                 )
        self.update_stats_widget(plot, True)
        display(self.m_widget.stats)

        legend.set_zoom_sel_handler(plot.backend.zoom_sel)
        legend.set_plot(plot)
        pass
    
    def handle_delete_trace(self, _):
        log.info("Delete Trace clicked")
        if (not self.model.delete_traces(self.m_widget.sw.value)):
            clear_output(wait=True)
            log.info("Refreshing")
            display(self.m_widget.widgets)
        self.update_select_widget()
        pass
