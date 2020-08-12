from ipywidgets import Text, Button, IntText
import os
import re
import sys
import subprocess

from settings import (
    BUTTON_LAYOUT,
    MONETA_BASE_DIR,
    MONETA_TOOL_DIR,
    OUTPUT_DIR,
    PIN_PATH,
    TOOL_PATH,
    WIDGET_DESC_PROP,
    WIDGET_LAYOUT,
    CWD_HISTORY_PATH
)
sys.path.append(MONETA_BASE_DIR + "moneta/moneta/")

import logging
log = logging.getLogger(__name__)

def button_factory(description, color='lightgray'):
    return Button(
            description=description,
            button_style='',
            layout = BUTTON_LAYOUT,
            style = {'button_color': color}
            )

def int_text_factory(value, description):
    return IntText(
            value=value,
            description=description,
            style=WIDGET_DESC_PROP,
            layout=WIDGET_LAYOUT
            )

def text_factory(placeholder, description):
    return Text(
            value='',
            placeholder=placeholder,
            description=description,
            style=WIDGET_DESC_PROP,
            layout=WIDGET_LAYOUT
            )

    
def parse_cwd(cwd_path):
    if cwd_path in ("/", "~", ".", ".."):
        return cwd_path
   
    # Assume '.' if there are no special path characters
    if not (cwd_path.startswith(("/", "~/", "./", "../"))):
        cwd_path = "./" + cwd_path;
    if cwd_path.endswith("/"):
        cwd_path = cwd_path[0:-1]
    return cwd_path

def parse_exec_input(e_input):
    exec_inputs = e_input.split(" ")
    exec_file_path = os.path.expanduser(exec_inputs[0])
    exec_args = exec_inputs[1:]

    # Pin sometimes doensn't run correctly if './' isn't specified
    if not (exec_file_path.startswith(("/", "~/", "./", "../"))):
        exec_file_path = "./" + exec_file_path; 

    return (exec_file_path, exec_args)
        
def load_cwd_file():
    try:
        with open(CWD_HISTORY_PATH, "a+") as history:
            history.seek(0)
            cwd_history = history.read().split()
            logging.debug("Reading history from file: {}".format(cwd_history))
            return cwd_history
    except Exception as e: 
        # Allows tool to still work, just no history, if there is a problem with the file
        log.debug("History file error: \n{}".format(e))
        return []
    
def update_cwd_file(cwd_history):
    with open(CWD_HISTORY_PATH, "w+") as history_file:
        for path in cwd_history:
            history_file.write(path + "\n")

            
def get_widget_values(m_widget):
    e_file, e_args = parse_exec_input(m_widget.ex.value)
    
    w_vals = {
        'c_lines': m_widget.cl.value,
        'c_block': m_widget.cb.value,
        'm_lines': m_widget.ml.value,
        'cwd_path': os.path.expanduser(parse_cwd(m_widget.cwd.value)),
        'e_file': e_file,
        'e_args': e_args,
        'o_name': m_widget.to.value,
        'is_full_trace': m_widget.ft.value
    }
    return w_vals
            
def verify_input(w_vals):
    log.info("Verifying pintool arguments")
  
    if (w_vals['c_lines'] <= 0 or w_vals['c_block'] <= 0 or w_vals['m_lines'] <= 0):
        print("Cache lines, cache block, and maximum lines to output must be greater than 0")
        return False
  
    if (len(w_vals['e_file']) == 0):
        print("Error: No executable provided")
        return False
  
    if (len(w_vals['o_name']) == 0):
        print("Error: No trace name provided")
        return False
  
    if not (re.search("^[a-zA-Z0-9_]*$", w_vals['o_name'])):
        print("Error: Output name can only contain alphanumeric characters and underscore")
        return False
  
    if (not os.path.isdir(w_vals['cwd_path'])):
        print("Directory '{}' not found".format(w_vals['cwd_path']))
        return False

    os.chdir(w_vals['cwd_path'])

    if (not os.path.isfile(w_vals['e_file'])):
        print("Executable '{}' not found".format(w_vals['e_file']))
        os.chdir(MONETA_TOOL_DIR)
        return False
  
    if (not os.access(w_vals['e_file'], os.X_OK)):
        print("\"{}\" is not an executable".format(w_vals['e_file']))
        os.chdir(MONETA_TOOL_DIR)
        return False
    
    os.chdir(MONETA_TOOL_DIR)
    return True


def run_pintool(w_vals):
    log.info("Running pintool")
  
    prefix = "full_trace_" if w_vals['is_full_trace'] else "trace_"
    # Temporary fix until Pintool handles double-open error
    if(os.path.isfile(OUTPUT_DIR + prefix + w_vals['o_name'] + ".hdf5")):
        subprocess.run(["rm", OUTPUT_DIR + prefix + w_vals['o_name'] + ".hdf5"]);
      
    is_full_trace_int = 1 if w_vals['is_full_trace'] else 0
  
    args_string = "" if len(w_vals['e_args']) == 0 else " " + " ".join(w_vals['e_args']) 
    print("Running \"{}{}\" in Directory \"{}\" with Cache Lines={} and Block Size={}B for Number of Lines={} into Trace: {}".format(
            w_vals['e_file'], args_string, w_vals['cwd_path'], w_vals['c_lines'], w_vals['c_block'], w_vals['m_lines'], w_vals['o_name']))
      
    args = [
        PIN_PATH, "-ifeellucky", "-injection", "child", "-t", TOOL_PATH,
        "-o", w_vals['o_name'],
        "-c", str(w_vals['c_lines']),
        "-m", str(w_vals['m_lines']),
        "-l", str(w_vals['c_block']),
        "-f", str(is_full_trace_int),
        "--", w_vals['e_file'], *w_vals['e_args']
    ]
    
    os.chdir(w_vals['cwd_path'])
    
    log.debug("Executable: {}".format(w_vals['e_file']))
    log.debug("Running in dir: {}".format(os.getcwd()))
    sub_output = subprocess.run(args, capture_output=True)
    sub_stdout = sub_output.stdout.decode('utf-8')
    sub_stderr = sub_output.stderr.decode('utf-8')
    log.debug("Raw pintool stdout: \n{}".format(sub_stdout))
    log.debug("Raw pintool stderr: \n{}".format(sub_stderr))
  
    os.chdir(MONETA_TOOL_DIR)
  
    if sub_stderr.startswith("Error"):
        print(sub_stderr)

def generate_trace(w_vals):
    if verify_input(w_vals):
        run_pintool(w_vals)
        print("Done generating trace: {}".format(w_vals['o_name']))
        return True
    return False


def collect_traces():
    """Reads output directory to fill up select widget with traces"""
    log.info("Reading outfile directory")
    trace_list = []
    trace_map = dict()
    dir_path, dir_names, file_names = next(os.walk(OUTPUT_DIR))
  
    for file_name in file_names:
        log.info("Checking {}".format(file_name))
        
        if (file_name.startswith("trace_") and file_name.endswith(".hdf5")):
            
            trace_name = file_name[6:file_name.index(".hdf5")]
            tag_path = os.path.join(dir_path, "tag_map_" + trace_name + ".csv")
            meta_path = os.path.join(dir_path, "meta_data_" + trace_name + ".txt")
            if not (os.path.isfile(tag_path) and os.path.isfile(meta_path)):
                print("Warning: Tag Map and/or Metadata file missing for {}. Omitting trace.".format(file_name))
                continue
          
            trace_list.append(trace_name)
            trace_map[trace_name] = (os.path.join(dir_path, file_name),
                                     tag_path, meta_path)
            log.debug("Trace: {}, Tag: {}".format(trace_name, tag_path))
        elif (file_name.startswith("full_trace_") and file_name.endswith(".hdf5")):
            trace_name = file_name[11:file_name.index(".hdf5")]
            tag_path = os.path.join(dir_path, "full_tag_map_" + trace_name + ".csv")
            meta_path = os.path.join(dir_path, "full_meta_data_" + trace_name + ".txt")
            if not (os.path.isfile(tag_path) and os.path.isfile(meta_path)):
                print("Warning: Tag Map and/or Metadata file missing for {}. Omitting full trace.".format(file_name))
                continue
            
            trace_list.append("(Full) " + trace_name)
            trace_map["(Full) " + trace_name] = (os.path.join(dir_path, file_name),
                                     tag_path, meta_path)
            log.debug("Trace: {}, Tag: {}".format("(" + trace_name + ")", tag_path))
    return trace_list, trace_map

def delete_traces(trace_paths):
    for trace_path, tag_path, meta_path in trace_paths:
        if (os.path.isfile(trace_path)):
            subprocess.run(['rm', trace_path])
        if (os.path.isfile(tag_path)):
            subprocess.run(['rm', tag_path])
        if (os.path.isfile(meta_path)):
            subprocess.run(['rm', meta_path])
