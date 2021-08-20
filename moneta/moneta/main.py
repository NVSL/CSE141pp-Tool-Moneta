
import argparse
import os
from importlib import reload
from moneta import Moneta
from moneta.ipyfilechooser import FileChooser
from moneta.settings import FC_FILTER, COLOR_VIEW, C_VIEW_OPTIONS
from moneta.utils import handle_load_trace, display_trace

def show_trace(trace_file):
    m = Moneta()
    display_trace(m, *os.path.split(trace_file))

def select_trace():
    m = Moneta()

    file_chooser = FileChooser(path=os.getcwd(), use_dir_icons=True, filter_pattern=FC_FILTER)
    file_chooser.register_callback(lambda self_fc: handle_load_trace(self_fc, m))
    display(file_chooser)

    
def main():
    parser = argparse.ArgumentParser(description='Process main.py flags')
    parser.add_argument('--color-view', default='All', choices=C_VIEW_OPTIONS, help="Change the color labeling options test")
    
    args = parser.parse_args()

    print(args.color_view)
    # set enviroment variable for color view options
    os.environ[COLOR_VIEW] = args.color_view
  
    select_trace();

if __name__ == '__main__':
    main()
