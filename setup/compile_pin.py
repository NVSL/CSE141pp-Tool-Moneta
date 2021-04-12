from contextlib import contextmanager
import subprocess
import argparse
import os

PIN_DIR = "/pin/source/tools/ManualExamples/"
PIN_TOOLS_DIR = "~/work/setup/pin_tools/"
OBJ_INTEL = "obj-intel64/"
TRACE_TOOLS = [
    "moneta_trace_tool.cpp",
    #"cfg_trace_tool.cpp"
]

def compile_tool(file_path, pin_path):
    full_file_path = os.path.expanduser(file_path)
    
    try:
        subprocess.run(["cp", full_file_path, pin_path], check=True)
    except:
        raise SystemExit

    if not os.path.isdir(pin_path + OBJ_INTEL):
        os.mkdir(pin_path + OBJ_INTEL)

    curr_dir = os.getcwd()
    os.chdir(os.path.expanduser(pin_path))
    
    pintool_so = full_file_path[full_file_path.rfind("/") + 1:-3] + "so"

    print("--------------------Running Pin---------------------")
    p = subprocess.run(["make", OBJ_INTEL + pintool_so, "TARGET=intel64"], capture_output=True)
    print("Stdout: ")
    print(p.stdout.decode())
    print("Stderr: ")
    stderr_output = p.stderr.decode()
    print(stderr_output)
    if len(stderr_output) > 0:
        raise SystemExit

    os.chdir(curr_dir)
    print(f"{file_path} done!")



parser = argparse.ArgumentParser(description="Input and Output for compiling pintool")
parser.add_argument('input', nargs='?', default=None)
args = parser.parse_args()
input_path = args.input

if not input_path:
    for tool in TRACE_TOOLS:
        compile_tool(PIN_TOOLS_DIR + tool, PIN_DIR)
else:
    if input_path.rfind(".cpp") == -1:
        print(f'Error: Not a cpp file - {input_path}')
        raise SystemExit

    compile_tool(input_path, PIN_DIR)

    
