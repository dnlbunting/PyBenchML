#!/usr/bin/env python

from .LFSGit import LFSRepo
from .configuration import loadConfig
from .environments import Environment
from .utils import filehash
from .results import results_main
from .run import run_main

import argparse,json
import os, pymongo, re
import os.path as path
from subprocess import Popen, PIPE
from hashlib import sha224
from shutil import rmtree
from time import sleep


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", 
                        help="The repository against which to run benchmarks")
                        
    parser.add_argument("repository", 
                        help="The repository against which to run benchmarks")
    
    parser.add_argument("--config", help="PBML configuration json, otherwise defaults to repository/config.json")
    parser.add_argument("--output", help="output")
    parser.add_argument("--overwrite", help="overwrite", action='store_true')
    
    args = parser.parse_args()
    
    # Load up the configuration
    if args.config is None:
        config = loadConfig(path.join(args.repository, "config.json"))
    else:
        config = loadConfig(args.config)
        
    
    dirs = {}
    dirs['repo']    = path.join(config['output_dir'], config['repo_dir'])
    dirs['db']      = path.join(config['output_dir'], config['db_dir'])
    dirs['env']     = path.join(config['output_dir'], config['env_dir'])
    dirs['results'] = path.join(config['output_dir'], config['results_dir'])
    dirs['script']  = path.join(path.dirname(__file__), "run_bench.py")
    
    
    if args.mode == "run":
        try:
            run_main(args, config, dirs)
        except:
            raise 
        finally:
            rmtree(dirs['repo'], ignore_errors=True)    
            
        
    elif args.mode == "results":
        results_main(args, config, dirs)
        

            
        
if __name__ == '__main__':
    main()
        
    
    


