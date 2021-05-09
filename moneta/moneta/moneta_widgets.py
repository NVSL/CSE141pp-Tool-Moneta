from moneta.ipyfilechooser import FileChooser
import os
from moneta.settings import FC_FILTER

class MonetaWidgets():
    def __init__(self):
        file_chooser = FileChooser(os.getcwd())
        file_chooser.use_dir_icons = True
        file_chooser.filter_pattern = FC_FILTER
        
        self.file_chooser = file_chooser
