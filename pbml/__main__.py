#!/usr/bin/env python

import argparse,json
from .LFSGit import LFSRepo
from .configuration import loadConfig
from .environments import Environment
from .utils import filehash
import os, pymongo, re
import os.path as path
from subprocess import Popen, PIPE
from hashlib import sha224
from shutil import rmtree
from time import sleep
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", 
                        help="The repository against which to run benchmarks")
    
    parser.add_argument("--config", help="PBML configuration json, otherwise defaults to repository/config.json")
    
    
    args = parser.parse_args()
    
    # Load up the configuration
    if args.config is None:
        config = loadConfig(path.join(args.repository, "config.json"))
    else:
        config = loadConfig(args.config)
        
    
    repo_dir = path.join(config['output_dir'], config['repo_dir'])
    db_dir = path.join(config['output_dir'], config['db_dir'])
    env_dir = path.join(config['output_dir'], config['env_dir'])
    results_dir = path.join(config['output_dir'], config['results_dir'])
    
    script = path.join(path.dirname(__file__), "run_bench.py")
    

    # Will hold the commits/benchmark combinations we need to run
    bm_todo = {}
    
    # Load the benchmark files
    benchmarks_dir = path.join(args.repository, config['benchmarks_dir'])
    bm_files = [(x, filehash(path.join(benchmarks_dir, x))) for x in os.listdir(benchmarks_dir) if re.match("\S+\.py$", x)]
    
    if path.isdir(config['output_dir']):
        # Output from previous run exists
        # TODO: Add validation
        
        # Start the db
        db, db_proc = db_start(db_dir)
        
        # Create a clone of the repo at the location in the config file  
        repo = LFSRepo(repo_dir, args.repository)
        
        bm_todo = {commit:[] for commit in repo.taggedCommits()}
                
        # Select only commit/benchmark combinations that don't already exist
        for commit in repo.taggedCommits():
            bm_todo[commit] = []            
            for bm_file_name, bm_file_hash  in bm_files:
                if db.benchmarks.find({"file_hash":bm_file_hash, "commit":commit}).count() < 1 :
                    bm_todo[commit].append((bm_file_name, bm_file_hash))
                    
                            
    else:
        print "Starting a new project"
        os.mkdir(config['output_dir'])
        
        # Create a clone of the repo at the location in the config file  
        repo = LFSRepo(repo_dir, args.repository)
                
        # Create the db and results folder 
        os.mkdir(db_dir)
        os.mkdir(results_dir)
        db, db_proc = db_start(db_dir)
        
        bm_todo = {commit:bm_files for commit in repo.taggedCommits()}
    
        
    # Run the selected BMs    
    for commit in bm_todo.keys():
        if bm_todo[commit] == []:
            continue
        # Create an environment to test this commit in 
        env = Environment(env_dir, [])
        
        for bm_file_name, bm_file_hash in bm_todo[commit]:
            
            # Spawn a subprocess to run a set of benchmarks in
            proc = env.run([script, path.join(benchmarks_dir, bm_file_name), commit], cwd=benchmarks_dir)
            stdoutdata, stderrdata = proc.communicate()
            
            if proc.returncode != 0:
                raise Exception("Failed running benchmark %s" % bm_file_name)
            for line in stdoutdata.split("\n"):
                if line is not '':
                    db.benchmarks.insert(json.loads(line))        
        
    
################################################################################

# Clean up section
    
    # Don't reuse the repo        
    rmtree(repo_dir)    

    # Make sure no zombies are left
    for k,v in locals().items():
        if isinstance(v, Popen):
            try:
                v.terminate()
                print "Terminated %s" % v
                
            except : 
                print "unable to terminate %s" % v
    


    

    
################################################################################
                

def parseBMFolder(path):
    # Filter out .py files
    pass
    
    

       

def db_start(db_dir):  
    db_process = Popen(["mongod", "--dbpath", db_dir, "--logpath", path.join(db_dir, "db.log")])        
    sleep(5)
    try:
        conn=pymongo.MongoClient()
    except pymongo.errors.ConnectionFailure, e:
       print "Could not connect to MongoDB: %s" % e   
     
    return conn.db, db_process  
        
if __name__ == '__main__':
    main()
        
    
    


