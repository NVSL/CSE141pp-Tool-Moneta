from moneta.ipyfilechooser import FileChooser
from IPython.display import clear_output, display
from moneta.settings import FC_FILTER, ERROR_LABEL
from moneta.model import Moneta
from moneta.utils import parse_zoom_args
import os

def select_trace(zoom_access=None, zoom_address=None):

    def handle_load_trace(file_chooser):
        clear_output(wait=True)
        display(file_chooser)

        print(f'Loading {file_chooser.selected_filename}\n')
        show_trace(file_chooser.selected, zoom_access, zoom_address)

    file_chooser = FileChooser(path=os.getcwd(), use_dir_icons=True, filter_pattern=FC_FILTER)
    file_chooser.register_callback(handle_load_trace)
    display(file_chooser)
    
def show_trace(trace_path, zoom_access=None, zoom_address=None, show_tag=None):
    if show_tag is not None:
        zoom_access = show_tag
        zoom_address = show_tag
        
    model = Moneta()
    err_message = model.load_trace(*os.path.split(trace_path))


    if err_message:
        print(err_message)
        return
        
    model.create_plot()

    if model.plot is None:
        print("Couldn't load plot")
        return

    if zoom_access or zoom_address:
        bounds = parse_zoom_args(model, zoom_access, zoom_address)

        if not bounds:
            print(f'{ERROR_LABEL} Invalid Zoom Arguments')
            print('Using default zoom...')
        else:
            model.plot.backend.zoom_sel(bounds[0][0], bounds[0][1], bounds[1][0], bounds[1][1])
        

    model.plot.show()
    model.legend.stats.update(init=True)
