
import argparse
import os
from importlib import reload
from moneta import Moneta
from moneta.ipyfilechooser import FileChooser
from moneta.settings import FC_FILTER
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
    args = parser.parse_args()

    select_trace();

if __name__ == '__main__':
    main()
