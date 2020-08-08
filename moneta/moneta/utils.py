from ipywidgets import Text, Button, IntText
import os
import re
import sys
import subprocess

from settings import (
    BUTTON_LAYOUT,
    MONETA_BASE_DIR,
    OUTPUT_DIR,
    PIN_PATH,
    TOOL_PATH,
    WIDGET_DESC_PROP,
    WIDGET_LAYOUT
)
sys.path.append(MONETA_BASE_DIR + "moneta/py_files/")

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

def verify_input(c_lines, c_block, m_lines, e_file, e_args, o_name, is_full_trace):
    log.info("Verifying pintool arguments")
  
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
  
    if (not os.access(e_file, os.X_OK)):
        print("\"{}\" is not an executable".format(e_file))
        return False
  
    return True


def run_pintool(c_lines, c_block, m_lines, e_file, e_args, o_name, is_full_trace):
    log.info("Running pintool")
  
    prefix = "full_trace_" if is_full_trace else "trace_"
    # Temporary fix until Pintool handles double-open error
    if(os.path.isfile(OUTPUT_DIR + prefix + o_name + ".hdf5")):
        subprocess.run(["rm", OUTPUT_DIR + prefix + o_name + ".hdf5"]);
      
    is_full_trace_int = 1 if is_full_trace else 0
  
    args_string = "" if len(e_args) == 0 else " " + " ".join(e_args) 
    print("Running \"{}{}\", Cache Lines={}, and Block Size={}B for Number of Lines={} into Trace: {}".format(e_file, args_string, c_lines, c_block, m_lines, o_name))
  
  
    dir_delimiter_index = e_file.rfind("/")
    if (dir_delimiter_index == -1):
        e_file = "./" + e_file
        dir_delimiter_index = 1
  
    curr_dir = os.getcwd()
    exec_dir = e_file[0:dir_delimiter_index + 1]
    exec_name = "./" + e_file[dir_delimiter_index + 1:len(e_file)]
    os.chdir(exec_dir)
      
    args = [
        PIN_PATH, "-ifeellucky", "-injection", "child", "-t", TOOL_PATH,
        "-o", o_name,
        "-c", str(c_lines),
        "-m", str(m_lines),
        "-l", str(c_block),
        "-f", str(is_full_trace_int),
        "--", exec_name, *e_args
    ]
    
    log.debug("Stripped Executable: {}".format(exec_name))
    log.debug("Running in dir: {}".format(os.getcwd()))
    sub_output = subprocess.run(args, capture_output=True)
    sub_stderr = sub_output.stderr.decode('utf-8')
    log.debug("Raw pintool stderr: \n{}".format(sub_stderr))
  
    os.chdir(curr_dir)
  
    if sub_stderr.startswith("Error"):
        print(sub_stderr)

def generate_trace(c_lines, c_block, m_lines, e_file, o_name, is_full_trace):
    exec_inputs = e_file.split(" ")
    exec_file = os.path.expanduser(exec_inputs[0])
    exec_args = exec_inputs[1:]
    next_args = [c_lines, c_block, m_lines, exec_file, exec_args, o_name, is_full_trace]
    if verify_input(*next_args):
        run_pintool(*next_args)
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