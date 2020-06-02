from ipywidgets import Text, Button, VBox, HBox, Layout, Checkbox, IntText, Label, Dropdown, SelectMultiple, ColorPicker
import os
import re
import sys
import vaex
import vaex.jupyter
import vaex.jupyter.plot
import argparse
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


parser = argparse.ArgumentParser(description='Display and control UI.')
parser.add_argument('-r', action='store_true',
                    help='When enabled, refresh to minimize cell output')
parser.add_argument('-log', action='store_true',
                    help='When enabled, Show debug/info logging')
args = parser.parse_args()

if not args.log:
  logging.disable(logging.CRITICAL) # To disable logger

# Constants
WIDGET_DESC_PROP = {'description_width': '150px'}
WIDGET_LAYOUT = Layout(width='90%')
BUTTON_LAYOUT = Layout(margin='15px 15px 0 15px',
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

# Original colors below
newc[1] = [0, 0, 1, 1] # read_hits - 1, .125
#newc[2] = [0, 0.7, 0, 1] # write_hits - 2, .25
newc[2] = [0, 1, 1, 1] # write_hits - 2, .25
newc[3] = [0.047, 1, 0, 1] # cache_size
newc[4] = [1, 1, 0, 1] # read_misses - 3, .375
#newc[5] = [1, 0, 0.2, 1] # write_misses - 4, .5
newc[5] = [1, 0, 0, 1] # write_misses - 4, .5
newc[6] = [0.737, 0.745, 0.235, 1] # compulsory read misses - 5, .625
newc[8] = [0.745, 0.309, 0.235, 1] # compulsory write misses - 6, .75
custom_cmap = ListedColormap(newc)

# Globals
trace_list = []
trace_map = dict()
trace_metadata = dict()
all_inputs = VBox()
currentSelection = [1,1,1,1,1,1]

select_widget = SelectMultiple(
    options=[],
    value=[],
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
  meta_prefix = "full_meta_data_" if is_full_trace else "meta_data_"
  with open(OUTPUT_DIR + meta_prefix + o_name + ".txt", 'w') as meta_f:
    meta_f.write(str(c_lines) + " " + str(c_block))


def gen_trace_controls():
  logging.info("Setting up generate trace widgets with handlers")
  cache_lines_widget = input_int_factory(4096, 'Cache Lines:')
  cache_block_widget = input_int_factory(64, 'Block Size (Bytes):')
  maximum_lines_widget = input_int_factory(100000000, 'Lines to Output:')
  executable_widget = input_text_factory('./Examples/build/sorting', 'Executable Path:')
  trace_out_widget = input_text_factory('baseline', 'Name for Output')

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
      read_out_dir()

      print("Done generating trace")
    logging.debug("Input Cache lines: {}".format(cache_lines_widget.value))

  gen_button.on_click(gen_trace)
  return (gen_trace_inputs, gen_button)

def read_out_dir():
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
      meta_path = os.path.join(dir_path, 'full_meta_data_' + trace_name + '.txt')
      if (not os.path.isfile(meta_path)):
        print("Warning: Metadata file missing for {}. Omitting full trace.".format(file_name))
        continue

      trace_list.append("(" + trace_name + ")")
      trace_map["(" + trace_name + ")"] = (os.path.join(dir_path, file_name),
                               None, meta_path)
      logging.debug("Trace: {}, Meta: {}".format("(" + trace_name + ")", meta_path))
    
        

  global select_widget
  select_widget.options = sorted(trace_list, key=str.casefold)
  select_widget.value = []

    
def generate_plot(trace_name):
  global df
  global tag_map
  global curr_trace
  if curr_trace != "":
    refresh()
  curr_trace = trace_name
  logging.info("Generating plot")

  trace_path, tag_path, meta_path = trace_map[trace_name]
  df = vaex.open(trace_path)
  if tag_path:
    logging.debug("Found a tag map file")
    tag_map = vaex.open(tag_path)
  else:
    logging.debug("No tag map -- Full trace")
  num_accesses = df.Address.count()
  df['index'] = np.arange(0, num_accesses)

  if len(tag_map.columns['Tag_Name']) == 0:
    print("No tags in file")
    return
  if tag_path:
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
  if tag_path:
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

  if tag_path:
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

      if(name.startswith("Reads")):
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
        combineSelections()
        
        currentSelection[targetHit-1] = 0
        currentSelection[targetMiss-1] = 0
        currentSelection[targetCMiss-1] = 0
        
    df.select('total')


  def updateHitMiss(change):
    if(change.name == 'value'):

      name = change.owner.description

      if(name.startswith("Hits")):
        targetRead = READ_HIT
        targetWrite = WRITE_HIT
      elif(name.startswith("Capacity")):
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
  
  def getCurrentView(self, frame):
    curView = frame[frame.index >= int(plot.limits[0][0])]
    curView = curView[curView.index <= int(plot.limits[0][1])+1]
    curView = curView[curView.Address >= int(plot.limits[1][0])]
    curView = curView[curView.Address <= int(plot.limits[1][1])+1]
    
    return curView
    
  def updateStats(self):
    curReadHits = getCurrentView(self,read_hits)
    curWriteHits = getCurrentView(self,write_hits)
    curReadMisses = getCurrentView(self,read_misses)
    curWriteMisses = getCurrentView(self,write_misses)
    curCompReadMisses = getCurrentView(self,comp_read_misses)
    curCompWriteMisses = getCurrentView(self,comp_write_misses)
    
    hitCount = curReadHits.count() + curWriteHits.count()
    missCount = curReadMisses.count() + curWriteMisses.count()
    compMissCount = curCompReadMisses.count() + curCompWriteMisses.count()
    totalCount = hitCount + missCount + compMissCount
    
    currentHitRate.value = "Hit Rate: "+f"{hitCount*100/totalCount:.2f}"+"%"
    currentCapMissRate.value = "Capacity Miss Rate: "+f"{missCount*100/totalCount:.2f}"+"%"
    currentCompMissRate.value = "Compulsory Miss Rate: "+f"{compMissCount*100/totalCount:.2f}"+"%"

  if tag_path:
    tagChecks = [HBox([Button(
                           icon='search-plus',
                           tooltip=name,
                           layout=Layout(height='35px', 
                                         width='35px', 
                                         border='none',
                                         align_items='center'
                                         ),
                                    style={'button_color': 'transparent'}
                           ),

                    Checkbox(description=name, 
                                     value=True, 
                                     disabled=False, 
                                     indent=False)
                    ])
               for name in namesFromFile]


  rwChecks = [Checkbox(description="Reads ("+str(readCount)+")", value=True, disabled=False, indent=False),
              Checkbox(description="Writes ("+str(writeCount)+")", value=True, disabled=False, indent=False)]

  hmChecks = [Checkbox(description="Hits ("+str(hitCount)+")", value=True, disabled=False, indent=False),
              Checkbox(description="Capacity Misses ("+str(missCount)+")", value=True, disabled=False, indent=False),
              Checkbox(description="Compulsory Misses ("+str(compMissCount)+")", value=True, disabled=False, indent=False)]

  hmRates = [Label(value="Total Trace Stats:", layout=Layout(width='200px')),
             Label(value="Hit Rate: "+f"{hitCount*100/df.count():.2f}"+"%"),
             Label(value="Capacity Miss Rate: "+f"{missCount*100/df.count():.2f}"+"%"),
             Label(value="Compulsory Miss Rate: "+f"{compMissCount*100/df.count():.2f}"+"%")]

  currentHitRate = Label(value="Hit Rate: "+f"{hitCount*100/df.count():.2f}"+"%")
  currentCapMissRate = Label(value="Capacity Miss Rate: "+f"{missCount*100/df.count():.2f}"+"%")
  currentCompMissRate = Label(value="Compulsory Miss Rate: "+f"{compMissCount*100/df.count():.2f}"+"%")
  currentHmRates = [Label(value="Trace Stats for Current View:", layout=Layout(width='200px')),
             currentHitRate, currentCapMissRate, currentCompMissRate]
  
  refreshRatesButton = Button(
          description='Refresh Stats',
          disabled=False,
          button_style='',
          layout= Layout(margin='10px 10px 0px 10px', width='200px', height='40px', border='1px solid black', flex='1'),
          style={'button_color': 'lightgray'},
          )
    
  if tag_path:
    for i in range(numTags):
      tagChecks[i].children[1].observe(updateGraph)
    
  for check in rwChecks:
    check.observe(updateReadWrite)
    
  for check in hmChecks:
    check.observe(updateHitMiss)
  
  
  refreshRatesButton.on_click(updateStats)
    
  if tag_path:
    checks = VBox([HBox([VBox(tagChecks), VBox(rwChecks), VBox(hmChecks)]), HBox([VBox(hmRates), VBox(currentHmRates), refreshRatesButton])])
  else:
    checks = VBox([HBox([VBox(rwChecks), VBox(hmChecks)]), HBox([VBox(hmRates), VBox(currentHmRates), refreshRatesButton])])


  def updateReadWrite2(change):
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
          else:
              df.select(df.Access == targetHit, mode='subtract', name='rw')
              df.select(df.Access == targetMiss, mode='subtract', name='rw')
              df.select(df.Access == targetCMiss, mode='subtract', name='rw')
              combineSelections()
      df.select('total')  
              
  def updateHitMiss2(change):
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
          else:
              df.select(df.Access == targetRead, mode='subtract', name='hm')
              df.select(df.Access == targetWrite, mode='subtract', name='hm')
              combineSelections()
      df.select('total')  
  from matplotlib.colors import to_rgba
  def updateColorMap(change):
      if(change.name=='value'):
          name=change.owner.name
          if(re.search('^Hits', name)):
              plot.colormap.colors[1] = to_rgba(change.new,1)
              plot.colormap.colors[2] = to_rgba(change.new,1)
          elif(re.search('^Cache', name)):
              plot.colormap.colors[3] = to_rgba(change.new,1)
          elif(re.search('^Capacity', name)):
              plot.colormap.colors[4] = to_rgba(change.new,1)
              plot.colormap.colors[5] = to_rgba(change.new,1)
          else:
              plot.colormap.colors[6] = to_rgba(change.new,1)
              plot.colormap.colors[8] = to_rgba(change.new,1)
  cb_lyt=Layout(width='180px')
  cp_lyt=Layout(width='30px')
  # Read Write custom checkbox
  def RWCheckbox(description, color_value):
      rwcp = ColorPicker(concise=True, value=color_value, disabled=False,layout=cp_lyt)
      rwcp.name=description
      return HBox([Checkbox(description=description, value=True, disabled=False, indent=False,layout=cb_lyt),
                  rwcp])

  with open(meta_path) as meta_f:
    mlines = meta_f.readlines()
    m_split = mlines[0].split()
    logging.debug("Reading meta data: {}".format(m_split))

  vaex_extended.vaex_cache_size = int(m_split[0])*int(m_split[1])

  from matplotlib.colors import to_hex
  rwChecks2 = [Checkbox(description="Reads ("+str(readCount)+")",  value=True, disabled=False, indent=False,layout=Layout(width='270px')),
              Checkbox(description="Writes ("+str(writeCount)+")",  value=True, disabled=False, indent=False,layout=Layout(width='270px'))]
  hmChecks2 = [RWCheckbox(description="Hits ("+str(hitCount)+")", color_value=to_hex([0, 0.5, 0])),
              RWCheckbox(description="Capacity Misses ("+str(missCount)+")", color_value=to_hex([1, 0.5, 0])),
              RWCheckbox(description="Compulsory Misses ("+str(compMissCount)+")", color_value=to_hex([0.235, 0.350, 0.745]))]
  cacheChecks2 = [RWCheckbox(description="Cache ("+str(int(m_split[0]) * int(m_split[1]))+" bytes)", color_value=to_hex([0, 0, 0]))]
  checks2 = VBox([VBox(children=[Label(value='Legend')] + rwChecks2 +  hmChecks2 + cacheChecks2,
                       layout=Layout(padding='10px',border='1px solid black')
                      )])
  for check in rwChecks2:
      check.observe(updateReadWrite2)
  for check in [hbox.children[0] for hbox in hmChecks2]:
      check.observe(updateHitMiss2)
  for colorpicker in [hbox.children[1] for hbox in hmChecks2]:
      colorpicker.observe(updateColorMap)

  plot = df.plot_widget(df.index, df.Address, what='max(Access)',
                 colormap = custom_cmap, selection=[True],
                 backend='bqplot_v2', tool_select=True, legend=checks2, type='custom_plot1')
  plot.backend.scale_x.observe(updateStats)
  plot.backend.scale_y.observe(updateStats)

  if tag_path:
    for i in range(numTags):
      tagChecks[i].children[0].on_click(plot.backend.zoomSection)
        
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
          description='Create Independent Subplot',
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
          description='Create Dependent Subplot',
          disabled=False,
          button_style='',
          layout= Layout(margin='10px 10px 0px 10px', width='200px', height='40px', border='1px solid black', flex='1'),
          style={'button_color': 'lightgray'},
          )
  dSubPlotButton.on_click(depSubPlot)
  display(dSubPlotButton)

  return


def run_load_button():
  load_button = button_factory('Load Trace', color='lightblue')
  def prepare_trace(_):
    if args.r:
      refresh()
    if len(select_widget.value) == 0:
      print("Error: No trace selected")
      return
    
    if len(select_widget.value) > 1:
      print("Error: Multiple traces selected, cannot load multiple traces")
      return
    generate_plot(select_widget.value[0])

  load_button.on_click(prepare_trace)
  return load_button


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
    
def del_trace_button():
  del_button = button_factory("Delete Trace", color='salmon')
  def delete_trace(_):
    logging.info("Deleting {}".format(select_widget.value))
    for selection in select_widget.value:
        delete_files(selection)
    read_out_dir()

  del_button.on_click(delete_trace)
  return del_button
    
def init_widgets():
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

  display(all_inputs)

    
def refresh():
  clear_output(wait=True)
  logging.info("Refreshing")
  display(all_inputs)

def main():
  logging.info("Setting up widgets")
  init_widgets()
  read_out_dir()


if __name__ == '__main__':
  main()
