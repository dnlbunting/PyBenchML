#!/usr/bin/env python

# Same hack as below 
from utils import filehash

import argparse
import os, inspect,sys,re
import os.path as path
from types import FunctionType
from timeit import timeit
import json


parser = argparse.ArgumentParser()
parser.add_argument("benchmark", 
                        help="The benchmark file to run")
parser.add_argument("commit", 
                        help="The commit hash")
args = parser.parse_args()

#print "Spawned benchmark %s for commit %s" % (args.benchmark, args.commit)

# Attempt to import the benchmark

# Bit of a hack because the spawned python seems to inherit the path of the parent so can't just import from cwd
sys.path.append(path.dirname(args.benchmark))
benchmark = __import__(path.basename(args.benchmark)[:-3], globals(), locals(), [], -1)
members = inspect.getmembers(benchmark) 


# Exctract the function type benchmarks
function_benchmarks =  [x for x in members if re.match("^benchmark_", x[0]) and isinstance(x[1], FunctionType )]

for fbm in function_benchmarks:
    times = [timeit(fbm[1], number=3)/3. for i in range(5)]
    print json.dumps({"commit":args.commit,
                      "file":path.basename(args.benchmark),
                      "file_hash": filehash(args.benchmark),
                      "benchmark":fbm[0],
                      "times":times,})