import subprocess
import os
from IPython.display import clear_output, display
from cse142.cfg.cfg_widgets import CFGWidgets
from cse142.cfg.edge_formatter import load_edges, generate_cfg
from cse142.settings import CFG_OUTPUT_DIR, CWD_HISTORY_FILE_NAME, HISTORY_MAX
from cse142.utils import collect_traces, generate_trace, update_cwd_file

class View():
    def __init__(self):
        self.init_widgets()

    def init_widgets(self):
        self.m_widget = CFGWidgets()
        self.m_widget.gb.on_click(self.handle_generate_trace)
        self.m_widget.lb.on_click(self.handle_load_trace)
        self.m_widget.db.on_click(self.handle_delete_trace)
        self.update_select_widget()
        
        display(self.m_widget.widgets)

    def update_select_widget(self):
        output_traces, _ = collect_traces(CFG_OUTPUT_DIR)
        self.m_widget.sw.options = sorted(output_traces, key=str.casefold)
        self.m_widget.sw.value = []

    def handle_generate_trace(self, _):
        w_vals = self.m_widget.get_widget_values()

        if generate_trace(w_vals, tool='cfg'):
            edges = load_edges()
            generate_cfg(edges, CFG_OUTPUT_DIR + w_vals['o_name'])
            self.update_cwd_widget(w_vals['display_path'])
            self.update_select_widget()

    def update_cwd_widget(self, cwd_path):
        if not cwd_path in (".", "./") and not cwd_path in self.m_widget.cwd.options:
            self.m_widget.cwd.options = [cwd_path, *self.m_widget.cwd.options][0:HISTORY_MAX]
            update_cwd_file(self.m_widget.cwd.options, CFG_OUTPUT_DIR, CWD_HISTORY_FILE_NAME)

    def handle_load_trace(self, _):
        print("TESTING")

    def handle_delete_trace(self, _):
        for trace in self.m_widget.sw.value:
            full_trace_path = CFG_OUTPUT_DIR + trace + '.pdf'
            if (os.path.isfile(full_trace_path)):
                subprocess.run(['rm', full_trace_path])

        clear_output(wait=True)
        display(self.m_widget.widgets)

        self.update_select_widget()



