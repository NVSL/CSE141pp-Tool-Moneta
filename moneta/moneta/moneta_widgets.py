from ipyfilechooser import FileChooser
import os
from moneta.settings import FC_WIDTH, FC_SCROLLBOX_HEIGHT, FC_FILTER

class MonetaWidgets():
    def __init__(self):
        file_chooser = FileChooser(os.getcwd())
        file_chooser.use_dir_icons = True
        file_chooser.filter_pattern = FC_FILTER

        file_chooser._trait_values['children'][1].layout.width = FC_WIDTH
        file_chooser._trait_values['children'][1].children[2].layout.height = FC_SCROLLBOX_HEIGHT
        
        self.file_chooser = file_chooser
