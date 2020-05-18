from imports import *

clear_output(wait=True)
display(inputs)
    
#Args for PIN
PIN_DIRECTORY = "/setup/pintool/pin.sh"
TOOL_DIRECTORY = "/setup/converter/trace_tool.so"
INFILE_EXECUTABLE = path.expanduser(infile.value)
OUTFILE_DIRECTORY = path.expanduser("/setup/converter/outfiles")
CACHE_SIZE = cache.value
NUM_LINES = lines.value
BLOCK_SIZE = block.value
   
err = False
 
if(CACHE_SIZE < 0 or NUM_LINES < 0 or BLOCK_SIZE < 0):
    print("Cache Lines, Lines to Output, and Block Size must be positive integers")
    err = True
    sys.exit() 
    
if(not path.isfile(INFILE_EXECUTABLE)):
    print("Executable \"{}\" Not Found".format(INFILE_EXECUTABLE))
    err = True
    sys.exit()


print("Running {} with Cache Lines={} and Block Size={}B for Number of Lines={}".format(INFILE_EXECUTABLE, CACHE_SIZE, BLOCK_SIZE, NUM_LINES))
    
args = [
    PIN_DIRECTORY,
    "-ifeellucky",
    "-injection",
    "child",
    "-t",
    TOOL_DIRECTORY,
    "-o",
    OUTFILE_DIRECTORY,
    "-c",
    str(CACHE_SIZE),
    "-m",
    str(NUM_LINES),
    "-l",
    str(BLOCK_SIZE),
    "--",
    INFILE_EXECUTABLE
]
    
try:
    df.close_files()
    tag_map.close_files()
except:
    pass

# Temporary fix until Pintool handles double-open error
if(path.isfile("/setup/converter/outfiles/trace.hdf5")):
    subprocess.run(["rm", "/setup/converter/outfiles/trace.hdf5"]);

subprocess.run(args,capture_output=True)
