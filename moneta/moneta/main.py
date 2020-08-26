import logging
from importlib import reload
reload(logging) # To display in Jupyter
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: [%(name)15s] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
#logging.disable(logging.CRITICAL) # To disable logging
import moneta.model as model
import moneta.view as view


def main():
    logger.info("Starting main")
    view.View(model.Model())
    pass

if __name__ == '__main__':
    main()
