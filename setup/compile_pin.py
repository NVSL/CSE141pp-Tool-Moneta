from contextlib import contextmanager
import subprocess
import argparse
import os

PIN_DIR = "/home/jovyan/pin/source/tools/ManualExamples/"
OBJ_INTEL = "obj-intel64/"
TRACE_TOOL = "/home/jovyan/work/setup/trace_tool.cpp"
OUTPUT_PATH = "/home/jovyan/work/setup/"

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

parser = argparse.ArgumentParser(description="Input and Output for compiling pintool")
parser.add_argument('input', nargs='?', default=TRACE_TOOL)
args = parser.parse_args()
curr_dir = os.getcwd()
input_path = args.input

if input_path.rfind(".cpp") == -1:
    print(f'Error: Not a cpp file - {input_path}')
    raise SystemExit

full_input_path = os.path.expanduser(input_path)
print("Using - " + full_input_path)

try:
    subprocess.run(["cp", full_input_path, PIN_DIR], check=True)
except:
    raise SystemExit

if not os.path.isdir(PIN_DIR+OBJ_INTEL):
    os.mkdir(PIN_DIR+OBJ_INTEL)

print("\n---------------Changing Directories-----------------")
with cd(PIN_DIR):

    full_input_path.rfind("/")
    pintool_so = full_input_path[full_input_path.rfind("/")+1:-3] + "so"
    print("--------------------Running Pin---------------------")
    p = subprocess.run(["make", "obj-intel64/" + pintool_so, "TARGET=intel64"], capture_output=True)
    print("Stdout: ")
    print(p.stdout.decode())
    print("Stderr: ")
    stderr_output = p.stderr.decode()
    print(stderr_output)
    if len(stderr_output) > 0:
        raise SystemExit
    print("Success!!")
