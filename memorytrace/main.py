from ipywidgets import Text, Button, VBox, HBox, Layout, Checkbox, IntText, Label, Dropdown, Select
import os
import re
import sys
import vaex
import vaex.jupyter
import vaex.jupyter.plot
import subprocess
import numpy as np
from matplotlib.colors import ListedColormap
from IPython.display import clear_output

sys.path.append('../')
import vaex_extended
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot', 'BqplotBackend')

import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#logging.disable(logging.CRITICAL) # To disable logger


# Constants
WIDGET_DESC_PROP = {'description_width': '150px'}
WIDGET_LAYOUT = Layout(width='90%')
BUTTON_LAYOUT = Layout(margin='10px 0 0 0',
    height='40px', width='90%', border='1px solid black')
BUTTON_STYLE = {'button_color': 'lightgray'}

DEFAULT_TRACE_DROP = 'Select a trace to load'

PIN_DIR  = "/setup/pintool/pin.sh"
TOOL_DIR = "/setup/converter/trace_tool.so"
OUTPUT_DIR = "/setup/converter/outfiles/"

#Enumerations
COMP_W_MISS = 6
COMP_R_MISS = 5
WRITE_MISS = 4
READ_MISS = 3
WRITE_HIT = 2
READ_HIT = 1

currentSelection = [1,1,1,1,1,1]

# Custom colormap
newc = np.ones((11, 4))
newc[1] = [0, 0.5, 0, 1] # read_hits - 1, .125
#newc[2] = [0, 0.7, 0, 1] # write_hits - 2, .25
newc[2] = [0, 0.5, 0, 1] # write_hits - 2, .25
newc[3] = [0, 0, 0, 1] # cache_size
newc[4] = [1, 0.5, 0, 1] # read_misses - 3, .375
#newc[5] = [1, 0, 0.2, 1] # write_misses - 4, .5
newc[5] = [1, 0.5, 0, 1] # write_misses - 4, .5
newc[6] = [0.235, 0.350, 0.745, 1] # compulsory read misses - 5, .625
newc[8] = [0.235, 0.350, 0.745, 1] # compulsory write misses - 6, .75

custom_cmap = ListedColormap(newc)




# Globals
trace_drop_list = [DEFAULT_TRACE_DROP]
trace_map = dict()
trace_metadata = dict()
trace_drop_widget = Dropdown(
    options=trace_drop_list,
    value=DEFAULT_TRACE_DROP,
    description="Trace:",
    layout=WIDGET_LAYOUT
    )

select_widget = Select(
    options=[],
    value=None,
    description='Trace:',
    layout=WIDGET_LAYOUT
)

df = 0
tag_map = 0
curr_trace = ""

def button_factory(desc, color='lightgray'):
  return Button(
          description=desc,
          button_style='',
          layout = BUTTON_LAYOUT,
          style = {'button_color': color}
         )

def input_int_factory(value, description):
  return IntText(
          value=value,
          description=description,
          style=WIDGET_DESC_PROP,
          layout=WIDGET_LAYOUT
         )

def input_text_factory(value, description):
  return Text(
          value=value,
          placeholder='',
          description=description,
          style=WIDGET_DESC_PROP,
          layout=WIDGET_LAYOUT
         )


def load_pin_controls():
  return

#def run_pintool(b):
#  print("hey")
#  print(dir(b))

def verify_input(c_lines, c_block, m_lines, e_path, o_name):
  logging.info("Verifying pintool arguments")
  if (c_lines <= 0 or c_block <= 0 or m_lines <= 0):
    print("Cache lines, cache block, and maximum lines to output must be > 0")
    return False

  if (not os.path.isfile(e_path)):
    print("Executable '{}' not found".format(e_path))
    return False

  if (len(o_name) == 0):
    print("Please provide trace name")
    return False
  # Add executable check
  return True

def run_pintool(c_lines, c_block, m_lines, e_path, o_name):
  logging.info("Running pintool")
  global df
  global tag_map
  try:
    df.close_files()
    tag_map.close_files()
  except:
    pass
  # Temporary fix until Pintool handles double-open error
  if(os.path.isfile(OUTPUT_DIR + "trace_" + o_name + ".hdf5")):
    subprocess.run(["rm", OUTPUT_DIR + "trace_" + o_name + ".hdf5"]);
  global curr_trace
  if (o_name == curr_trace):
    curr_trace = ""
    refresh()
  print("Running {} with Cache Lines={} and Block Size={}B for Number of Lines={} into trace: {}".format(e_path, c_lines, c_block, m_lines, o_name))
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
      "--",
      e_path
  ]
  sub_output = subprocess.run(args, capture_output=True)
  sub_output = sub_output.stderr.decode('utf-8')
  logging.debug("Raw pintool output: \n{}".format(sub_output))
  with open(OUTPUT_DIR + "meta_data_" + o_name + ".txt", 'w') as meta_f:
    meta_f.write(str(c_lines) + " " + str(c_block))

  return

def gen_trace_controls():
  logging.info("Setting up generate trace widgets with handlers")
  cache_lines_widget = input_int_factory(4096, 'Cache Lines:')
  cache_block_widget = input_int_factory(64, 'Block Size (Bytes):')
  maximum_lines_widget = input_int_factory(100000000, 'Lines to Output:')
  executable_widget = input_text_factory('./Examples/build/sorting', 'Executable Path:')
  trace_out_widget = input_text_factory('baseline', 'Name for Output')

  gen_button = button_factory('Generate Trace', color='darkseagreen')

  gen_trace_inputs = VBox([cache_lines_widget,
                     cache_block_widget,
                     maximum_lines_widget,
                     executable_widget,
                     trace_out_widget,
                     gen_button],
                     layout=Layout(width="100%"))

  def gen_trace(_):
    widget_vals = [cache_lines_widget.value,
                    cache_block_widget.value,
                    maximum_lines_widget.value,
                    executable_widget.value,
                    trace_out_widget.value]
    #global trace_metadata
    #trace_metadata
    if verify_input(*widget_vals):
      run_pintool(*widget_vals)
      read_out_dir()

      print("Done generating trace")
    logging.debug("Input Cache lines: {}".format(cache_lines_widget.value))

  gen_button.on_click(gen_trace)
  return gen_trace_inputs

def read_out_dir():
  logging.info("Reading outfile directory")
  global trace_drop_list
  global trace_map
  trace_drop_list = [trace_drop_list[0]]
  trace_map = dict()
  dir_path, dir_names, file_names = next(os.walk(OUTPUT_DIR))
  for file_name in file_names:
    logging.info("Checking {}".format(file_name))
    if file_name.startswith('trace_') and file_name.endswith('.hdf5'):
      trace_name = file_name[6:file_name.index('.hdf5')]
      tag_path = os.path.join(dir_path, 'tag_map_' + trace_name + '.csv')
      meta_path = os.path.join(dir_path, 'meta_data_' + trace_name + '.txt')
      if os.path.isfile(tag_path) and os.path.isfile(meta_path):
        trace_drop_list.append(trace_name)
        trace_map[trace_name] = (os.path.join(dir_path, file_name),
                                 tag_path, meta_path)
        logging.debug("Trace: {}, Tag: {}".format(trace_name, tag_path))

  global trace_drop_widget
  global select_widget
  trace_drop_widget.options = trace_drop_list
  trace_drop_widget.value = DEFAULT_TRACE_DROP if curr_trace == '' else curr_trace
  select_widget.options = trace_drop_list[1:]
  select_widget.value = None if len(trace_drop_list) == 1 else trace_drop_list[1] 

def generate_plot(trace_name):
  global df
  global tag_map
  global curr_trace
  curr_trace = trace_name
  refresh()
  logging.info("Generating plot")

  trace_path, tag_path, meta_path = trace_map[trace_name]
  df = vaex.open(trace_path)
  tag_map = vaex.open(tag_path)
  num_accesses = df.Address.count()
  df['index'] = np.arange(0, num_accesses)

  #Set up name-tag mapping
  namesFromFile = (tag_map.Tag_Name.values).tolist()
  tagsFromFile = (tag_map.Tag_Value.values).tolist()
  startIndices = (tag_map.First_Access.values).tolist()
  startAddresses = (tag_map.Low_Address.values).tolist()
  endIndices = (tag_map.Last_Access.values).tolist()
  endAddresses = (tag_map.High_Address.values).tolist()

  numTags = len(namesFromFile)
  logging.debug("Number of tags: {}".format(numTags))
  logging.debug("Tags: {}".format(namesFromFile))


  # Initialize accessRanges dictionary in bqplot backend with file info
  from vaex_extended.jupyter.bqplot import accessRanges
  accessRanges.clear()
  for i in range(numTags):
    name = namesFromFile[i]
    accessRanges.update({name : {}})

    rangeData = accessRanges[name]
    rangeData.update({"startIndex" : startIndices[i]})
    rangeData.update({"endIndex" : endIndices[i]})
    rangeData.update({"startAddr" : startAddresses[i]})
    rangeData.update({"endAddr" : endAddresses[i]})




  #Define all selections here
  df.select(True, name='structures')
  df.select(True, name='rw')
  df.select(True, name='hm')
  df.select(True, name='total')

  #Initialize counts
  read_hits = df[df.Access == READ_HIT]
  write_hits = df[df.Access == WRITE_HIT]
  read_misses = df[df.Access == READ_MISS]
  write_misses = df[df.Access == WRITE_MISS]
  comp_read_misses = df[df.Access == COMP_R_MISS]
  comp_write_misses = df[df.Access == COMP_W_MISS]
  readCount = read_hits.count() + read_misses.count()
  writeCount = write_hits.count() + write_misses.count()
  hitCount = read_hits.count() + write_hits.count()
  missCount = read_misses.count() + write_misses.count()
  compMissCount = comp_read_misses.count() + comp_write_misses.count()

  #Initialize selections
  for tag in tagsFromFile:
    df.select(df.Tag == tag, mode='or')


  #Handle all boolean combinations of independent checkboxes here
  def combineSelections():
    df.select("structures", mode='replace', name='total')
    df.select("rw", mode='and', name='total')
    df.select("hm", mode='and', name='total')

  def updateGraph(change):
    if(change.name == 'value'):

      name = change.owner.description
      tag = tagsFromFile[namesFromFile.index(name)]

      if(change.new == True):
        df.select(df.Tag == tag, mode='or', name='structures')
        combineSelections()
      else:
        df.select(df.Tag == tag, mode='subtract', name='structures')
        combineSelections()
    df.select('total')



  def updateReadWrite(change):
    if(change.name == 'value'):

      name = change.owner.description
      

      if(re.search('^Reads', name)):
        targetHit = READ_HIT
        targetMiss = READ_MISS
        targetCMiss = COMP_R_MISS

      else:
        targetHit = WRITE_HIT
        targetMiss = WRITE_MISS
        targetCMiss = COMP_W_MISS

      if(change.new == True):
        df.select(df.Access == targetHit, mode='or', name='rw')
        df.select(df.Access == targetMiss, mode='or', name='rw')
        df.select(df.Access == targetCMiss, mode='or', name='rw')
        combineSelections()

        currentSelection[targetHit-1] = 1
        currentSelection[targetMiss-1] = 1
        currentSelection[targetCMiss-1] = 1
      else:
        df.select(df.Access == targetHit, mode='subtract', name='rw')
        df.select(df.Access == targetMiss, mode='subtract', name='rw')
        df.select(df.Access == targetCMiss, mode='subtract', name='rw')
        currentSelection[targetHit-1] = 0
        currentSelection[targetMiss-1] = 0
        currentSelection[targetCMiss-1] = 0
        combineSelections()
    df.select('total')

        
  def updateHitMiss(change):
    if(change.name == 'value'):

      name = change.owner.description

      if(re.search('^Hits', name)):
        targetRead = READ_HIT
        targetWrite = WRITE_HIT
      elif(re.search('^Capacity', name)):
        targetRead = READ_MISS
        targetWrite = WRITE_MISS
      else:
        targetRead = COMP_R_MISS
        targetWrite = COMP_W_MISS

      if(change.new == True):
        df.select(df.Access == targetRead, mode='or', name='hm')
        df.select(df.Access == targetWrite, mode='or', name='hm')
        combineSelections()
        
        currentSelection[targetRead-1] = 1
        currentSelection[targetWrite - 1] = 1
      else:
        df.select(df.Access == targetRead, mode='subtract', name='hm')
        df.select(df.Access == targetWrite, mode='subtract', name='hm')
        combineSelections()
        
        currentSelection[targetRead-1] = 0
        currentSelection[targetWrite - 1] = 0
        
    df.select('total')


  tagButtons = [Checkbox(description=name, value=True, disabled=False, indent=False) for name in namesFromFile]

  rwButtons = [Checkbox(description="Reads ("+str(readCount)+")", value=True, disabled=False, indent=False),
               Checkbox(description="Writes ("+str(writeCount)+")", value=True, disabled=False, indent=False)]

  hmButtons = [Checkbox(description="Hits ("+str(hitCount)+")", value=True, disabled=False, indent=False),
               Checkbox(description="Capacity Misses ("+str(missCount)+")", value=True, disabled=False, indent=False),
               Checkbox(description="Compulsory Misses ("+str(compMissCount)+")", value=True, disabled=False, indent=False)]

  hmRates = [Label(value="Hit Rate: "+f"{hitCount*100/df.count():.2f}"+"%"),
             Label(value="Miss Rate: "+f"{missCount*100/df.count():.2f}"+"%"),
             Label(value="Compulsory Miss Rate: "+f"{compMissCount*100/df.count():.2f}"+"%")]

  for i in range(numTags):
    tagButtons[i].observe(updateGraph)

  for button in rwButtons:
    button.observe(updateReadWrite)

  for button in hmButtons:
    button.observe(updateHitMiss)

  checks = VBox([HBox([VBox(tagButtons), VBox(rwButtons), VBox(hmButtons)]),VBox(hmRates)])

  with open(meta_path) as meta_f:
    mlines = meta_f.readlines()
    m_split = mlines[0].split()
    logging.debug("Reading meta data: {}".format(m_split))
  vaex_extended.vaex_cache_size = int(m_split[0])*int(m_split[1])

  plot = df.plot_widget(df.index, df.Address, what='max(Access)',
                 colormap = custom_cmap, selection=[True],
                 backend='bqplot_v2', tool_select=True, type='custom_plot1')
    
  display(checks)


  def selectDF(inDF):
    if(currentSelection[READ_MISS-1] == 1):
        inDF.select(inDF.Access == READ_MISS, mode='or')
    if(currentSelection[READ_HIT-1] == 1):
        inDF.select(inDF.Access == READ_HIT, mode='or')
    if(currentSelection[COMP_R_MISS-1] == 1):
        inDF.select(inDF.Access == COMP_R_MISS, mode='or')
    if(currentSelection[WRITE_MISS-1] == 1):
        inDF.select(inDF.Access == WRITE_MISS, mode='or')
    if(currentSelection[WRITE_HIT-1] == 1):
        inDF.select(inDF.Access == WRITE_HIT, mode='or')
    if(currentSelection[COMP_W_MISS-1] == 1):
        inDF.select(inDF.Access == COMP_W_MISS, mode='or')

    # Create a duplicate plot with current limits as the initial state of plot
  def indSubPlot(b):
      dfNew = vaex.from_pandas(df)
      #intial selection not functioning, diplays all data from original df
      dfNew.plot_widget(dfNew.index, dfNew.Address, what='max(Access)', colormap = custom_cmap, backend='bqplot_v2', tool_select=True, selection=True, limits=plot.limits, type='custom_plot1')
      selectDF(dfNew)

  indSubPlotButton = Button(
          description='Create Indepenent Subplot',
          disabled=False,
          button_style='',
          layout= Layout(margin='10px 10px 0px 10px', width='200px', height='40px', border='1px solid black', flex='1'),
          style={'button_color': 'lightgray'},
          )
  indSubPlotButton.on_click(indSubPlot)
  display(indSubPlotButton)

  def depSubPlot(b):
      df.plot_widget(df.index, df.Address, what='max(Access)', colormap = custom_cmap, backend='bqplot_v2', tool_select=True, selection=plot.selection, limits=plot.limits,type='custom_plot1')


  dSubPlotButton = Button(
          description='Create Depenent Subplot',
          disabled=False,
          button_style='',
          layout= Layout(margin='10px 10px 0px 10px', width='200px', height='40px', border='1px solid black', flex='1'),
          style={'button_color': 'lightgray'},
          )
  dSubPlotButton.on_click(depSubPlot)
  display(dSubPlotButton)
  return





def run_load_controls():
  logging.info("Setting up load widgets with handlers")
  read_out_dir()
  global trace_drop_widget
  load_button = button_factory('Load Trace', color='lightblue')
  load_inputs = VBox([trace_drop_widget,
                load_button],
                layout=Layout(width="100%", justify_content="space-between"))

  def prepare_trace(_):
    if trace_drop_widget.value == DEFAULT_TRACE_DROP:
      print("Please pick a trace")
      return
    generate_plot(trace_drop_widget.value)

  load_button.on_click(prepare_trace)
  return load_inputs

def delete_files(trace_name):
  logging.info("Deleting files for {}".format(trace_name))
  trace_path, tag_path, meta_path = trace_map[trace_name]
  subprocess.run(["rm", trace_path]) # Should error check
  subprocess.run(["rm", tag_path])
  subprocess.run(["rm", meta_path])
  trace_drop_list.remove(trace_name)
  trace_drop_widget.options = trace_drop_list
  global curr_trace
  logging.debug("Change current trace? {} == {}".format(trace_name, curr_trace))
  if (trace_name == curr_trace):
    curr_trace = ""
    trace_drop_widget.value = DEFAULT_TRACE_DROP
    refresh()
  elif (curr_trace != ""):
    trace_drop_widget.value = curr_trace


def display_all():
  gen_trace_inputs = gen_trace_controls()
  load_inputs = run_load_controls()
    

  delete_widget = button_factory("Delete Trace", color='salmon')

  def delete_trace(_):
    logging.info("Deleting {}".format(select_widget.value))
    conv_list = list(select_widget.options)
    if (len(conv_list) == 0):
      return
    delete_files(select_widget.value)
    select_widget.options = trace_drop_list[1:]

  delete_widget.on_click(delete_trace)

  del_inputs = VBox([select_widget, delete_widget],
      layout=Layout(width="100%", justify_content="space-between"))
  all_inputs = HBox([gen_trace_inputs, load_inputs, del_inputs],
                    layout=Layout(justify_content="space-around"))

  display(all_inputs)

def refresh():
  clear_output(wait=True)
  display_all()

def main():
  logging.info("Setting up widgets")
  display_all()

if __name__ == '__main__':
  main()
