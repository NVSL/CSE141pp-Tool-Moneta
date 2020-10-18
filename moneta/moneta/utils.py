from ipywidgets import Text, Button, IntText, Label
import os
import re
import sys
import subprocess

from moneta.settings import (
    TextStyle,
    ERROR_LABEL,
    WARNING_LABEL,
    BUTTON_LAYOUT,
    MONETA_BASE_DIR,
    MONETA_TOOL_DIR,
    OUTPUT_DIR,
    PIN_PATH,
    TOOL_PATH,
    WIDGET_DESC_PROP,
    WIDGET_LAYOUT,
    CWD_HISTORY_PATH,
    INDEX,
    ADDRESS,
    COMP_W_MISS,
    COMP_R_MISS,
    WRITE_MISS,
    READ_MISS,
    WRITE_HIT,
    READ_HIT
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

def parse_exec_input(e_input):
    exec_inputs = e_input.split(" ")
    exec_file_path = os.path.expanduser(exec_inputs[0])
    exec_args = exec_inputs[1:]

    # Pin sometimes doesn't run correctly if './' isn't specified
    if not (exec_file_path.startswith(("/", "~/", "./", "../"))):
        exec_file_path = "./" + exec_file_path; 

    return (exec_file_path, exec_args)
        


def load_cwd_file():
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
        log.debug(f"Making output dir")
    try:
        with open(CWD_HISTORY_PATH, "a+") as history:
            history.seek(0)
            cwd_history = history.read().split()
            log.debug(f"Reading history from file: {cwd_history}")
            return cwd_history
    except Exception as e: 
        # Allows tool to still work, just no history, if there is a problem with the file
        log.debug(f"History file error: \n{e}")
        return []
    
def update_cwd_file(cwd_history):
    with open(CWD_HISTORY_PATH, "w+") as history_file:
        for path in cwd_history:
            history_file.write(path + "\n")


def get_curr_stats(plot):
    
    df = plot.dataset
    
    x_min = f'({INDEX} >= {int(plot.limits[0][0])})'
    x_max = f'({INDEX} <= {int(plot.limits[0][1])})'
    y_min = f'({ADDRESS} >= {int(plot.limits[1][0])})'
    y_max = f'({ADDRESS} <= {int(plot.limits[1][1])})'
    
    # Inner df returns an expression, doesn't actually create the new dataframe
    df = df[df[f'{x_min} & {x_max} & {y_min} & {y_max}']]
    
    # Limit min/max is min/max value of Access enum, shape is number of types of access
    stats = df.count(binby=['Access'], limits=[1,7], shape=6)
    
    hit_count = stats[READ_HIT - 1] + stats[WRITE_HIT - 1]
    cap_miss_count = stats[READ_MISS - 1] + stats[WRITE_MISS - 1]
    comp_miss_count = stats[COMP_R_MISS - 1] + stats[COMP_W_MISS - 1]
    total_count = hit_count + cap_miss_count + comp_miss_count

    return total_count, hit_count, cap_miss_count, comp_miss_count

def update_legend_view_stats(plot_stats, plot, is_init):
    total_count, hit_count, cap_miss_count, comp_miss_count = get_curr_stats(plot)

    if(is_init):
        plot_stats.total_hits.value = stats_hit_string(hit_count, total_count)
        plot_stats.total_cap_misses.value = stats_cap_miss_string(cap_miss_count, total_count)
        plot_stats.total_comp_misses.value = stats_comp_miss_string(comp_miss_count, total_count)

    plot_stats.curr_hits.value = stats_hit_string(hit_count, total_count)
    plot_stats.curr_cap_misses.value = stats_cap_miss_string(cap_miss_count, total_count)
    plot_stats.curr_comp_misses.value = stats_comp_miss_string(comp_miss_count, total_count)

def stats_percent(count, total):
    return 'N/A' if total == 0 else f'{count*100/total:.2f}'+'%'
def stats_hit_string(count, total):
    return 'Hits: '+ str(count) + ' (' + stats_percent(count, total) +')'
def stats_cap_miss_string(count, total):
    return 'Cap. Misses: '+ str(count) + ' (' + stats_percent(count, total) +')'
def stats_comp_miss_string(count, total):
    return 'Comp. Misses: '+ str(count) + ' (' + stats_percent(count, total) +')'
    






def parse_cwd(path):
    """ Returns a final path and an absolute path
        Final path is either an absolute path, relative from home,
        or relative from current directory depending on closest parent of the three
        NOTE: Assumes '..' is not part of a file name
    """

    path = path or '.'
    expanded = os.path.expanduser(path.strip())
    realpath = os.path.realpath(expanded)
    home_rel = os.path.relpath(expanded, start='/home/jovyan')
    curr_rel = os.path.relpath(expanded)
    
    if ".." in home_rel:
        return realpath, realpath
    
    if ".." in curr_rel:
        if home_rel == '.':
            return "~", realpath
        return "~/" + home_rel, realpath
    
    return curr_rel, realpath
            
def verify_input(w_vals):
    log.info("Verifying pintool arguments")
    w_vals['display_path'], w_vals['cwd_path'] = parse_cwd(w_vals['cwd_path'])
  
    if (w_vals['c_lines'] <= 0 or w_vals['c_block'] <= 0 or w_vals['m_lines'] <= 0):
        print(f"{ERROR_LABEL} {TextStyle.RED}Cache lines, cache block, and output lines to output must be greater than 0{TextStyle.END}")
        return False
  
    if (len(w_vals['e_file']) == 0):
        print(f"{ERROR_LABEL} {TextStyle.RED}No executable provided{TextStyle.END}")
        return False
  
    if (len(w_vals['o_name']) == 0):
        print(f"{ERROR_LABEL} {TextStyle.RED}No trace name provided{TextStyle.END}")
        return False
  
    if not (re.search("^[a-zA-Z0-9_]*$", w_vals['o_name'])):
        print(f"{ERROR_LABEL} {TextStyle.RED}Output name can only contain alphanumeric characters and underscore{TextStyle.END}")
        return False
  
    if (not os.path.isdir(w_vals['cwd_path'])):
        print(f"{ERROR_LABEL} {TextStyle.RED}Directory '{w_vals['cwd_path']}' not found{TextStyle.END}")
        return False

    os.chdir(w_vals['cwd_path'])

    if (not os.path.isfile(w_vals['e_file'])):
        print(f"{ERROR_LABEL} {TextStyle.RED}Executable '{w_vals['e_file']}' not found{TextStyle.END}")
        os.chdir(MONETA_TOOL_DIR)
        return False
  
    if (not os.access(w_vals['e_file'], os.X_OK)):
        print(
              f"{ERROR_LABEL} {TextStyle.RED}\"{w_vals['e_file']}\" is not an executable{TextStyle.END}")
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
    track_main_int = 1 if w_vals['track_main'] else 0
  
    args_string = "" if len(w_vals['e_args']) == 0 else " " + " ".join(w_vals['e_args']) 

    args = [
        PIN_PATH, "-ifeellucky", "-injection", "child", "-t", TOOL_PATH,
        "-name", w_vals['o_name'],
        "-cache_lines", str(w_vals['c_lines']),
        "-output_lines", str(w_vals['m_lines']),
        "-block", str(w_vals['c_block']),
        "-full", str(is_full_trace_int),
        "-main", str(track_main_int),
        "--", w_vals['e_file'], *w_vals['e_args']
    ]

    print(f"{TextStyle.BOLD}Running in Directory:{TextStyle.END} \"{w_vals['cwd_path']}\" \n"
          f"{TextStyle.BOLD}Pintool Command:{TextStyle.END} {' '.join(args)}\n")
    
    os.chdir(w_vals['cwd_path'])
    
    log.debug(f"Executable: {w_vals['e_file']}")
    log.debug(f"Running in dir: {os.getcwd()}")
    sub_output = subprocess.run(args, capture_output=True)
    sub_stdout = sub_output.stdout.decode('utf-8')
    sub_stderr = sub_output.stderr.decode('utf-8')
    log.debug(f"Raw pintool stdout: \n{sub_stdout}")
    log.debug(f"Raw pintool stderr: \n{sub_stderr}")
  
    os.chdir(MONETA_TOOL_DIR)
  
    if sub_stderr:
        print(f"{TextStyle.RED}An error occurred while running your program. "
              f"This is normally caused by Tag typos and/or stopping invalid Tags. "
              f"Double check your program and Pin tags to make sure they are correct.\n\n"
              f"{TextStyle.RED}{TextStyle.BOLD}Raw Error Message:\n{TextStyle.END}"
              f"{TextStyle.RED}{sub_stderr}{TextStyle.END}")
        return False
    return True




def generate_trace(w_vals):
    if verify_input(w_vals) and run_pintool(w_vals):

        border_char = '#'
        side = border_char * 5
        done = f"{side} Done generating trace: {w_vals['o_name']} {side}"
        border = border_char * len(done)

        print(f"{TextStyle.GREEN}{TextStyle.BOLD}{border}\n"
              f"{done}\n"
              f"{border}{TextStyle.END}\n")
        return True
    return False


def collect_traces():
    """Reads output directory to fill up select widget with traces"""
    log.info("Reading outfile directory")
    trace_list = []
    trace_list_full = []

    trace_map = {}
    if not os.path.isdir(OUTPUT_DIR):
        return [], [], {}
    dir_path, dir_names, file_names = next(os.walk(OUTPUT_DIR))
  
    for file_name in file_names:
        log.info(f"Checking {file_name}")
        
        if (file_name.startswith("trace_") and file_name.endswith(".hdf5")):
            
            trace_name = file_name[6:file_name.index(".hdf5")]
            tag_path = os.path.join(dir_path, "tag_map_" + trace_name + ".csv")
            meta_path = os.path.join(dir_path, "meta_data_" + trace_name + ".txt")
            if not (os.path.isfile(tag_path) and os.path.isfile(meta_path)):
                print(f"{WARNING_LABEL} {TextStyle.YELLOW}Tag Map and/or Metadata file missing for {file_name}. Omitting trace.{TextStyle.END}")
                continue
          
            trace_list.append(trace_name)
            trace_map[trace_name] = (os.path.join(dir_path, file_name),
                                     tag_path, meta_path)
            log.debug(f"Trace: {trace_name}, Tag: {tag_path}")
        elif (file_name.startswith("full_trace_") and file_name.endswith(".hdf5")):
            trace_name = file_name[11:file_name.index(".hdf5")]
            tag_path = os.path.join(dir_path, "full_tag_map_" + trace_name + ".csv")
            meta_path = os.path.join(dir_path, "full_meta_data_" + trace_name + ".txt")
            if not (os.path.isfile(tag_path) and os.path.isfile(meta_path)):
                print(f"{WARNING_LABEL} {TextStyle.YELLOW}Tag Map and/or Metadata file missing for {file_name}. Omitting full trace.{TextStyle.END}")
                continue
            
            trace_list_full.append(trace_name)
            trace_map["(Full) " + trace_name] = (os.path.join(dir_path, file_name),
                                     tag_path, meta_path)
            log.debug("Trace: {}, Tag: {}".format("(" + trace_name + ")", tag_path))
    return trace_list, trace_list_full, trace_map 


def delete_traces(trace_paths):
    for trace_path, tag_path, meta_path in trace_paths:
        if (os.path.isfile(trace_path)):
            subprocess.run(['rm', trace_path])
        if (os.path.isfile(tag_path)):
            subprocess.run(['rm', tag_path])
        if (os.path.isfile(meta_path)):
            subprocess.run(['rm', meta_path])
