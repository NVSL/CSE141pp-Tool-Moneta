#!/usr/bin/env python3

import logging as log
import argparse
import textwrap
import sys
import subprocess
import platform
import os

def main() :
    parser = argparse.ArgumentParser(description=textwrap.dedent("""Gather a trace for Moneta"""))

    parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Be verbose")
    parser.add_argument('--trace', default="trace", help="Trace name")
    parser.add_argument('--cache-line-size', default=64, help="Cache line size")
    parser.add_argument('--cache-line-count', default=512, help="Cache line count")
    parser.add_argument('cmd', nargs=argparse.REMAINDER,  help="Command to run")
    parser.add_argument('--main', default="main", help="Function to start tracing at")
    parser.add_argument('--memops', default=10000000, help="how many accesses to trace")
    parser.add_argument('--file-count', default=1, help="How many trace files to create, if needed.")
    parser.add_argument('--skip', default=1000000000000, help="How many memops to skip")
    parser.add_argument('--debug', default=False, action='store_true', help="Pause pin so you can connect with gdb")
    parser.add_argument('--flush-cache-on-new-file', default=False, action='store_true', help="Flush the cache when you open a new file?");


    args = parser.parse_args(sys.argv[1:])

    if not args.verbose:
        log.basicConfig(format="%(levelname)-8s %(message)s", level=log.WARN)
    else:
        log.basicConfig(format="{} %(levelname)-8s [%(filename)s:%(lineno)d]  %(message)s".format(platform.node()) if args.verbose else "%(levelname)-8s %(message)s",
                        level=log.DEBUG if args.verbose else log.WARN)


    if os.environ.get("OMP_NUM_THREADS"):
        log.warn("-------------")
        log.warn("Overriding OMP_NUM_THREADS by setting it to 1")
        log.warn("-------------")
        os.environ["OMP_NUM_THREADS"] = "1"

    pin_cmd =f"/pin/pin.sh -ifeellucky -injection child "
    tool_cmd=f"-t /pin/source/tools/ManualExamples/obj-intel64/trace_tool.so -name {args.trace} -file_count {args.file_count} -cache_lines {args.cache_line_count} -block {args.cache_line_size} -start {args.main} -ol {args.memops} -stack_size {int(1e12)} -skip {args.skip}"
    if args.debug:
        pin_cmd += " -pause_tool 30"
    if args.flush_cache_on_new_file:
        tool_cmd += " -flush-cache-on-new-file"
    app_cmd = ' '.join(args.cmd[1:])
    run_cmd = f"{pin_cmd} {tool_cmd} -- {app_cmd}"

    files = [f"{args.trace}.meta",
             f"{args.trace}.tags",
             f"{args.trace}.hdf5"]

    for f in files:
        try:
            print(f"Removing {f}")
            os.unlink(f)
        except:
            pass

    log.info(f"Cache size: {args.cache_line_count} lines * {int(args.cache_line_size)} bytes/Line = {int(args.cache_line_count) * int(args.cache_line_size)} KB")
        
    print(f"Running: {run_cmd}")
    subprocess.run(run_cmd.split())
