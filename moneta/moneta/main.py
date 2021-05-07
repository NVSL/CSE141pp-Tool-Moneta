import logging
import argparse
from importlib import reload
reload(logging) # To display in Jupyter
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: [%(name)15s] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
import moneta.model as model
import moneta.view as view


def main():
    parser = argparse.ArgumentParser(description='Process main.py flags')
    parser.add_argument('--log', '-l', action='store_true', help='When enabled, show debug/info logging')
    args = parser.parse_args()

    if not args.log:
        logging.disable(logging.CRITICAL)

    logger.info("Starting main")
    view.View(model.Model())


if __name__ == '__main__':
    main()
