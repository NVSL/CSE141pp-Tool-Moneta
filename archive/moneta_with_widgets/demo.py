#!/usr/bin/env python3
import moneta_tags as moneta
import random
import argparse
import sys


t = None
m = {}
sum = 0
def op_rand(args):
    global t
    print(f"in {op_rand}")
    t = [random.random() for _ in range(0,args.size)]

def op_sort(args):
    global t
    t.sort()

def op_shuffle(args):
    global t
    random.shuffle(t)

def op_zero(args):
    global t
    t = [_ for _ in range(0,args.size)]

def op_hash(args):
    global t, m
    for i in t:
        m[i] = i

def op_search(args):
    global t, m,sum

    for i in t:
        sum += m[i]

def op_update(args):
    global t, m

    for i in t:
        m[i]+= 4

def op_del(args):
    global t, m

    for i in t:
        del m[i]


def main(argv):
    parser = argparse.ArgumentParser()

    ops = [x[3:] for x in globals() if "op_" in x]
    
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Be verbose")
    parser.add_argument('--op', nargs="+", default="rand",choices=ops, help="Operation to perform")
    parser.add_argument('--size', default=100000, type=int, help="how much data to operate on")
    
    args = parser.parse_args(argv)
    
    moneta.START_TRACE()
    for op in args.op: 
        print(f"Running {op}")

        moneta.DUMP_START_ALL(op, True);
        globals()["op_"+op](args)
        moneta.DUMP_STOP(op)
    #    moneta.STOP_TRACE()
        
if __name__ == "__main__":
    main(sys.argv[1:])
