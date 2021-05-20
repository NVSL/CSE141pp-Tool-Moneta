from moneta.ipyfilechooser import FileChooser
from IPython.display import clear_output, display
from moneta.settings import FC_FILTER
from moneta.model import Moneta
from moneta.utils import validate_zoom_args
import os

def select_trace(zoom=None):

    def handle_load_trace(file_chooser):
        clear_output(wait=True)
        display(file_chooser)

        print(f'Loading {file_chooser.selected_filename}\n')
        show_trace(file_chooser.selected, zoom)

    file_chooser = FileChooser(path=os.getcwd(), use_dir_icons=True, filter_pattern=FC_FILTER)
    file_chooser.register_callback(handle_load_trace)
    display(file_chooser)
    
def show_trace(trace_path, zoom=None):
    model = Moneta()
    err_message = model.load_trace(*os.path.split(trace_path))

    if err_message:
        print(err_message)
        return

    model.create_plot()

    if model.plot is None:
        print("Couldn't load plot")
        return

    if(zoom):
        err_message = validate_zoom_args(zoom)
        if err_message:
            print(err_message)
            print('Using default zoom...')
        else:
            model.plot.backend.zoom_sel(zoom[0][0], zoom[0][1], zoom[1][0], zoom[1][1])
        

    model.plot.show()
    model.legend.stats.update(init=True)