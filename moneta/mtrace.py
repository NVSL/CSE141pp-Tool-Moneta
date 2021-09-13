
import logging as log
import argparse
import textwrap
import sys
import subprocess
import platform
import os
import click

@click.command()
@click.option("--verbose", "-v", is_flag=True, default=False, help="Be verbose")
@click.option("--trace", type=str, default="trace", help="trace name")
@click.option("--cache-line-size", type=int, default=64, help="Cache line size")
@click.option("--cache-line-count", type=int, default=512, help="cache line count")
@click.option("--main", type=str, default="main", help="Function to trace")
@click.option("--memops", default=10000000, help="How many memory operations to trace")
@click.option("--file-count", default=1, type=int, help="How many trace files to collect")
@click.option("--skip", default=0, type=int, help="How many memops to skip")
@click.option("--debug", is_flag=True, default=False, help="Pause so you can attach a debugger")
@click.option("--tagged-only", is_flag=True, default=False, help="Only record tagged accesses.")
@click.option("--flush-cache-on-new-file", is_flag=True, default=False, help="Flush cache when you open a new file")
@click.argument("cmd", nargs=-1)
def mtrace(*argc, **kwargs) :
    do_mtrace(*argc, **kwargs)
    
def do_mtrace(*argc, **args):

    verbose = args.pop("verbose", False)
    trace =  args.pop("trace", "trace")
    cache_line_count = args.pop("cache_line_count", 512)
    cache_line_size = args.pop("cache_line_size", 64)
    main = args.pop("main", "main")
    memops = args.pop("memops", 10000000)
    file_count = args.pop("file_count", 1)
    skip = args.pop("skip", 0)
    debug = args.pop("debug", False)
    flush_cache_on_new_file = args.pop("flush_cache_on_new_file", False)
    cmd = args.pop("cmd")
    jupyter = args.pop("jupyter", True)
    tagged_only = args.pop("tagged_only", False)
    if not verbose:
        log.basicConfig(format="%(levelname)-8s %(message)s", level=log.WARN)
    else:
        log.basicConfig(format="{} %(levelname)-8s [%(filename)s:%(lineno)d]  %(message)s".format(platform.node()) if verbose else "%(levelname)-8s %(message)s",
                        level=log.DEBUG if verbose else log.WARN)

    if os.environ.get("OMP_NUM_THREADS"):
        log.warn("-------------")
        log.warn("Overriding OMP_NUM_THREADS by setting it to 1")
        log.warn("-------------")
        os.environ["OMP_NUM_THREADS"] = "1"

    pin_cmd =f"{os.environ['PIN_ROOT']}pin.sh -ifeellucky -injection child "
    tool_cmd=f"-t {os.environ['PIN_ROOT']}source/tools/ManualExamples/obj-intel64/trace_tool.so -name {trace} -file_count {file_count} -cache_lines {cache_line_count} -block {cache_line_size} -start {main} -ol {memops}  -skip {skip}" + (" -tagged-only" if tagged_only else "")
    if debug:
        pin_cmd += " -pause_tool 30"
    if flush_cache_on_new_file:
        tool_cmd += " -flush-cache-on-new-file"

    app_cmd = ' '.join(cmd)

    run_cmd = f"{pin_cmd} {tool_cmd} -- {app_cmd}"

    files = [f"{trace}.meta",
             f"{trace}.tags",
             f"{trace}.hdf5"]

    for f in files:
        try:
            if not jupyter:
                log.info(f"Removing {f}")
            os.unlink(f)
        except:
            pass

    print(f"Running: {run_cmd}")
    if not jupyter:
        log.info(f"Cache size: {cache_line_count} lines * {int(cache_line_size)} bytes/Line = {int(cache_line_count) * int(cache_line_size)} KB")
    subprocess.run(run_cmd.split())

