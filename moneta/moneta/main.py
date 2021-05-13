
import argparse
from importlib import reload
import moneta.model as model
import moneta.view as view

def show_trace(trace_file):
    view.View(model.Model()).load_file(trace_file)

def select_trace():
    view.View(model.Model(), file_chooser=True)
    
def main():
    parser = argparse.ArgumentParser(description='Process main.py flags')
    args = parser.parse_args()

    view.View(model.Model(), file_chooser=True)


if __name__ == '__main__':
    main()
