
import argparse
from importlib import reload
import moneta.model as model
import moneta.view as view


def main():
    parser = argparse.ArgumentParser(description='Process main.py flags')
    args = parser.parse_args()

    view.View(model.Model())


if __name__ == '__main__':
    main()
