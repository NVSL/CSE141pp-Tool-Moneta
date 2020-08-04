from . import configure, load, plot
from .imports import *
import logging

class Moneta():
    def __init__(self):
        self.widget = self.create_widget()
    def create_widget(self):
        logging.info("Intializing widgets")
        #gen_trace_inputs, gen_button = gen_trace_controls()
        #load_button = run_load_button()
        #del_button = del_trace_button()

        #trace_widgets = HBox([gen_trace_inputs, select_widget],
        #                layout=Layout(justify_content="space-around"))

        #buttons = HBox([gen_button, load_button, del_button])
        configurer = configure.MonetaConfigurer()
        loader = load.MonetaLoader()
        configurer.link_loader(loader)
        #global all_inputs
        self.all_inputs = HBox([configurer.widget, loader.widget],
                        layout=Layout(justify_content="space-around")
                        )

        display(self.all_inputs)
        return self.all_inputs

def main():
  logging.info("Setting up widgets")
  #init_widgets()
  create_widgets()
  read_out_dir()


if __name__ == '__moneta__':
  main()






"""def init_widgets():
  logging.info("Intializing widgets")
  gen_trace_inputs, gen_button = gen_trace_controls()
  load_button = run_load_button()
  del_button = del_trace_button()

  trace_widgets = HBox([gen_trace_inputs, select_widget],
                    layout=Layout(justify_content="space-around"))

  buttons = HBox([gen_button, load_button, del_button])

  global all_inputs
  all_inputs = VBox([trace_widgets, buttons],
                    layout=Layout(justify_content="space-around")
                   )

  display(all_inputs)"""