#from . import imports
from .imports import *


#sys.path.append('/setup/') # For master branch
sys.path.append('../.setup/')
import vaex_extended
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot', 'BqplotBackend')


def verify_input(c_lines, c_block, m_lines, e_file, e_args, o_name, is_full_trace):
  logging.info("Verifying pintool arguments")

  if (c_lines <= 0 or c_block <= 0 or m_lines <= 0):
    print("Cache lines, cache block, and maximum lines to output must be greater than 0")
    return False

  if (len(e_file) == 0):
    print("Error: No executable provided")
    return False

  if (len(o_name) == 0):
    print("Error: No trace name provided")
    return False

  if not (re.search("^[a-zA-Z0-9_]*$", o_name)):
    print("Error: Output name can only contain alphanumeric characters and underscore")
    return False

  if (not os.path.isfile(e_file)):
    print("Executable '{}' not found".format(e_file))
    return False

  if(not os.access(e_file, os.X_OK)):
    print("\"{}\" is not an executable".format(e_file))
    return False

  return True



def run_pintool(c_lines, c_block, m_lines, e_file, e_args, o_name, is_full_trace):
  logging.info("Running pintool")
  global df
  global tag_map

  try:
    df.close_files()
    tag_map.close_files()
  except:
    pass

  prefix = "full_trace_" if is_full_trace else "trace_"
  # Temporary fix until Pintool handles double-open error
  if(os.path.isfile(OUTPUT_DIR + prefix + o_name + ".hdf5")):
    subprocess.run(["rm", OUTPUT_DIR + prefix + o_name + ".hdf5"]);
    
  global curr_trace
  logging.debug("Current trace is: {}".format(curr_trace))
  if (o_name == curr_trace):
    curr_trace = ""
    refresh()
    

  is_full_trace_int = 1 if is_full_trace else 0

  args_string = "" if len(e_args) == 0 else " " + " ".join(e_args) 
  print("Running \"{}{}\", Cache Lines={}, and Block Size={}B for Number of Lines={} into Trace: {}".format(e_file, args_string, c_lines, c_block, m_lines, o_name))

  args = [
      PIN_DIR,
      "-ifeellucky",
      "-injection",
      "child",
      "-t",
      TOOL_DIR,
      "-o",
      o_name,
      "-c",
      str(c_lines),
      "-m",
      str(m_lines),
      "-l",
      str(c_block),
      "-f",
      str(is_full_trace_int),
      "--",
      e_file,
      *e_args
  ]
  sub_output = subprocess.run(args, capture_output=True)
  sub_stderr = sub_output.stderr.decode('utf-8')
  logging.debug("Raw pintool stderr: \n{}".format(sub_stderr))


  if sub_stderr.startswith("Error"):
    print(sub_stderr)

  meta_prefix = "full_meta_data_" if is_full_trace else "meta_data_"
  with open(OUTPUT_DIR + meta_prefix + o_name + ".txt", 'w') as meta_f:
    meta_f.write(str(c_lines) + " " + str(c_block))




class MonetaConfigurer():
    def __init__(self):
        gen_trace_inputs, gen_button = self.gen_trace_controls()
        self.widget = VBox([gen_trace_inputs, gen_button])
        self.loader = None

    def link_loader(self,loader):
      self.loader = loader

    def gen_trace_controls(self):
      logging.info("Setting up generate trace widgets with handlers")
      cache_lines_widget = input_int_factory(4096, 'Cache Lines:')
      cache_block_widget = input_int_factory(64, 'Block Size (Bytes):')
      maximum_lines_widget = input_int_factory(100000000, 'Lines to Output:')
      executable_widget = input_text_factory('e.g. ./Examples/build/sorting', 'Executable Path:')
      trace_out_widget = input_text_factory('e.g. baseline', 'Name for Output')

      full_trace = Checkbox(description="Trace everything (Ignore tags)?",
                            value=False, indent=False)


      gen_trace_inputs = VBox([cache_lines_widget,
                              cache_block_widget,
                              maximum_lines_widget,
                              executable_widget,
                              trace_out_widget,
                              full_trace],
                              layout=Layout(width="100%"))

      gen_button = button_factory('Generate Trace', color='darkseagreen')
      def gen_trace(_):
        if args.r:
          refresh()
        exec_inputs = executable_widget.value.split(" ")
        exec_file = exec_inputs[0]
        exec_args = exec_inputs[1:]
        
        widget_vals = [cache_lines_widget.value,
                      cache_block_widget.value,
                      maximum_lines_widget.value,
                      exec_file,
                      exec_args,
                      trace_out_widget.value,
                      full_trace.value]

        if verify_input(*widget_vals):
          run_pintool(*widget_vals)
          if (self.loader):
            self.loader.read_out_dir()

          print("Done generating trace")
        logging.debug("Input Cache lines: {}".format(cache_lines_widget.value))

      gen_button.on_click(gen_trace)
      return (gen_trace_inputs, gen_button)