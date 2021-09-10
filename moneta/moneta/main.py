
import argparse
import os
from settings import *
from moneta import select_trace, show_trace

def main():
    parser = argparse.ArgumentParser(description='Process main.py flags')
    parser.add_argument('--color-view', default='None', choices=C_VIEW_OPTIONS, help="Change the color labeling options test")
    
    args = parser.parse_args()

    print(args.color_view)
    # set enviroment variable for color view options
    os.environ[COLOR_VIEW] = args.color_view
  
    select_trace()

if __name__ == '__main__':
    main()
