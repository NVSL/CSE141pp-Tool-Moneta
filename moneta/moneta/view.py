from IPython.display import clear_output, display
from moneta.moneta_widgets import MonetaWidgets
from moneta.legend.legend import Legend
import vaex
import vaex.jupyter.plot
vaex.jupyter.plot.backends['moneta_backend'] = ("moneta.vaextended.bqplot", "BqplotBackend")


class View():
    def __init__(self, model):
        self.model = model
        self.init_widgets()

    def init_widgets(self):
        self.m_widget = MonetaWidgets()
        self.m_widget.file_chooser.register_callback(self.handle_load_trace)
        display(self.m_widget.file_chooser)

    def handle_load_trace(self):
        self.model.ready_next_trace()
        clear_output(wait=True)
        display(self.m_widget.file_chooser)

        path = self.m_widget.file_chooser.selected_path
        trace_name = self.m_widget.file_chooser.selected_filename
        print(f'Loading {trace_name}\n')

        err_message = self.model.load_trace(path, trace_name)

        if err_message is not None:
            print(err_message)
            return

        self.model.create_plot()

        if self.model.plot is None:
            print("Couldn't load plot")
            return

        self.model.plot.show()
        self.model.legend.stats.update(init=True)
