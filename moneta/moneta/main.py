
import argparse
from moneta import select_trace, show_trace

def main():
    parser = argparse.ArgumentParser(description='Process main.py flags')
    args = parser.parse_args()

    select_trace();

if __name__ == '__main__':
    main()
