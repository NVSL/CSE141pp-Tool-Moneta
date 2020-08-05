import subprocess
PIN_DIR = "/pin/source/tools/ManualExamples/"
TRACE_TOOL = "~/work/.setup/trace_tool.cpp"
OUTPUT_PATH = "~/work/.setup/"

from contextlib import contextmanager
import os

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

curr_dir = os.getcwd() + "/"
print("Enter input file and output directory. Press enter for defaults")
print()
print("Default input [" + TRACE_TOOL + "]")
input_path = input(">> Enter path to pintool file: ")

if len(input_path) == 0:
    input_path = TRACE_TOOL
else:
    if input_path.rfind(".cpp") == -1:
        print("Error: Not a cpp file")
        raise SystemExit
    if input_path[0] != "/":
        input_path = curr_dir + input_path

full_input_path = os.path.expanduser(input_path)
print("Using - " + full_input_path)

print()
print("Default output dir [" + OUTPUT_PATH + "]")
output_path = input(">> Enter path to store .so file: ")

if len(output_path) == 0:
    output_path = OUTPUT_PATH
elif output_path[0] != "/":
    output_path = curr_dir + output_path

if output_path[-1] != "/":
    output_path+="/"

full_output_path = os.path.expanduser(output_path)
print("Using - " + full_output_path)

subprocess.run(["cp", full_input_path, PIN_DIR], check=True)
print()
print("---------------Changing Directories-----------------")

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

    print("---------------Copying to output dir----------------")
    subprocess.run(["cp", PIN_DIR+"obj-intel64/"+pintool_so, full_output_path], check=True)
