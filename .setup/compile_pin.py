from contextlib import contextmanager
import subprocess
import argparse
import os

PIN_DIR = "/pin/source/tools/ManualExamples/"
TRACE_TOOL = "~/work/.setup/trace_tool.cpp"
OUTPUT_PATH = "~/work/.setup/"

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
parser.add_argument('output_dir', nargs='?', default=OUTPUT_PATH)
args = parser.parse_args()
input_path = args.input
output_path = args.output_dir

if input_path.rfind(".cpp") == -1:
    print(f'Error: Not a cpp file - {input_path}')
    raise SystemExit

full_input_path = os.path.expanduser(input_path)
print("Using - " + full_input_path)

if output_path[-1] != "/":
    output_path+="/"

full_output_path = os.path.expanduser(output_path)
print("Using - " + full_output_path)

try:
    subprocess.run(["cp", full_input_path, PIN_DIR], check=True)
except:
    raise SystemExit

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

    print("---------------Copying to output dir----------------")
    try:
        subprocess.run(["cp", PIN_DIR+"obj-intel64/"+pintool_so, full_output_path], check=True)
    except:
        raise SystemExit
    print("Success!!")
