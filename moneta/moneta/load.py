from .imports import *
from .plot import MonetaPlot

def delete_files(trace_name):
  logging.info("Deleting files for {}".format(trace_name))
  trace_path, tag_path, meta_path = trace_map[trace_name]
    
  global curr_trace
  if (trace_name == curr_trace):
    curr_trace = ""
    refresh()
    
  if(os.path.isfile(trace_path)):
    subprocess.run(["rm", trace_path])
  if(tag_path and os.path.isfile(tag_path)):
    subprocess.run(["rm", tag_path])
  if(os.path.isfile(meta_path)):
    subprocess.run(["rm", meta_path])
    

class MonetaLoader():
  def __init__(self):
      self.select_widget = SelectMultiple(
          options=[],
          value=[],
          description='Trace:',
          layout=WIDGET_LAYOUT
      )
      self.read_out_dir()
      load_button = self.run_load_button()
      del_button = self.del_trace_button()
      self.widget = VBox([self.select_widget,HBox([load_button, del_button])],layout=Layout(width='500px'))

  def read_out_dir(self):
    """Reads output directory to fill up select widget with traces"""
    logging.info("Reading outfile directory")
    global trace_list
    global trace_map
    trace_list = []
    trace_map = dict()
    dir_path, dir_names, file_names = next(os.walk(OUTPUT_DIR))

    for file_name in file_names:
      logging.info("Checking {}".format(file_name))
      
      if (file_name.startswith('trace_') and file_name.endswith('.hdf5')):
          
        trace_name = file_name[6:file_name.index('.hdf5')]
        tag_path = os.path.join(dir_path, 'tag_map_' + trace_name + '.csv')
        meta_path = os.path.join(dir_path, 'meta_data_' + trace_name + '.txt')
        if not (os.path.isfile(tag_path) and os.path.isfile(meta_path)):
          print("Warning: Tag Map and/or Metadata file missing for {}. Omitting trace.".format(file_name))
          continue

        trace_list.append(trace_name)
        trace_map[trace_name] = (os.path.join(dir_path, file_name),
                                tag_path, meta_path)
        logging.debug("Trace: {}, Tag: {}".format(trace_name, tag_path))
      elif (file_name.startswith('full_trace_') and file_name.endswith('.hdf5')):
        trace_name = file_name[11:file_name.index('.hdf5')]
        tag_path = os.path.join(dir_path, 'full_tag_map_' + trace_name + '.csv')
        meta_path = os.path.join(dir_path, 'full_meta_data_' + trace_name + '.txt')
        if not (os.path.isfile(tag_path) and os.path.isfile(meta_path)):
          print("Warning: Tag Map and/or Metadata file missing for {}. Omitting full trace.".format(file_name))
          continue

        trace_list.append("(" + trace_name + ")")
        trace_map["(" + trace_name + ")"] = (os.path.join(dir_path, file_name),
                                tag_path, meta_path)
        logging.debug("Trace: {}, Tag: {}".format("(" + trace_name + ")", tag_path))
      
          

    #global select_widget
    self.select_widget.options = sorted(trace_list, key=str.casefold)
    self.select_widget.value = []


  def run_load_button(self):
    load_button = button_factory('Load Trace', color='lightblue')
    def prepare_trace(_):
      if args.r:
        refresh()
      if len(self.select_widget.value) == 0:
        print("Error: No trace selected")
        return
      
      if len(self.select_widget.value) > 1:
        print("Error: Multiple traces selected, cannot load multiple traces")
        return
      
      #generate_plot(self.select_widget.value[0])
      trace_path, tag_path, meta_path = trace_map[self.select_widget.value[0]]
      plot = MonetaPlot(trace_path, tag_path, meta_path, self.select_widget.value[0])

    load_button.on_click(prepare_trace)
    return load_button


  def del_trace_button(self):
    del_button = button_factory("Delete Trace", color='salmon')
    def delete_trace(_):
      logging.info("Deleting {}".format(self.select_widget.value))
      for selection in self.select_widget.value:
          delete_files(selection)
      self.read_out_dir()

    del_button.on_click(delete_trace)
    return del_button