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
    parser.add_argument('--cache-line-size', default="64", help="Cache line size")
    parser.add_argument('--cache-line-count', default="4096", help="Cache line count")
    parser.add_argument('cmd', nargs=argparse.REMAINDER,  help="Command to run")
    parser.add_argument('--main', default="main", help="Function to start tracing at")
    parser.add_argument('--memops', default=10000000, help="how many accesses to trace")

    args = parser.parse_args(sys.argv[1:])

    if not args.verbose:
        log.basicConfig(format="%(levelname)-8s %(message)s", level=log.WARN)
    else:
        log.basicConfig(format="{} %(levelname)-8s [%(filename)s:%(lineno)d]  %(message)s".format(platform.node()) if args.verbose else "%(levelname)-8s %(message)s",
                        level=log.DEBUG if args.verbose else log.WARN)


    run_cmd=f"/pin/pin.sh -ifeellucky -injection child -t /pin/source/tools/ManualExamples/obj-intel64/trace_tool.so -name {args.trace} -c {args.cache_line_count} -cache_lines {args.cache_line_size} -start {args.main} -ol {args.memops} -stack_size {int(1e12)} -- {' '.join(args.cmd[1:])}"

    files = [f"meta_data_{args.trace}.txt",
             f"tag_map_{args.trace}.csv",
             f"trace_{args.trace}.hdf5"]

    for f in files:
        try:
            print(f"Removing {f}")
            os.unlink(f)
        except:
            pass

    print(f"Running: {run_cmd}")
    subprocess.run(run_cmd.split())
