
import argparse, json
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

        
def run_main(args, config, dirs):    
    
    # Load the benchmark files
    dirs['benchmarks'] = path.join(args.repository, config['benchmarks_dir'])
    bm_files = [(x, filehash(path.join(dirs['benchmarks'], x))) for x in os.listdir(dirs['benchmarks']) if re.match("\S+\.py$", x)]
   
    if path.isdir(config['output_dir']) and (args.overwrite is False):
        bm_todo, db, db_proc = existing_project(args, config, dirs, bm_files)                    
    else:
        rmtree(config['output_dir'], ignore_errors=True)
        bm_todo, db, db_proc = new_project(args, config, dirs, bm_files)
    
    try:
        procs = []
        procs = benchmark(bm_todo, dirs, db)
    except:
        db_proc.terminate()
        for p in procs:
            p.terminate()
        raise
        
    
################################################################################

# Clean up section
    
    # Don't reuse the repo        
    db_proc.terminate()

################################################################################
            
 
def new_project(args, config, dirs, bm_files):
    """docstring for new_project"""
    
    print "Starting a new project"
    os.mkdir(config['output_dir'])
    
    # Create a clone of the repo at the location in the config file  
    repo = LFSRepo(dirs['repo'], args.repository)
            
    # Create the db and results folder 
    os.mkdir(dirs['db'])
    os.mkdir(dirs['results'])
    db, db_proc = db_start(dirs['db'])
    
    bm_todo = {commit:bm_files for commit in repo.taggedCommits()}
    
    return bm_todo, db, db_proc
    
def existing_project(args, config, dirs, bm_files):
    
    # Output from previous run exists
    # TODO: Add validation
    
    # Start the db
    db, db_proc = db_start(dirs['db'])
    
    # Create a clone of the repo at the location in the config file  
    repo = LFSRepo(dirs['repo'], args.repository)
    
    bm_todo = {commit:[] for commit in repo.taggedCommits()}
            
    # Select only commit/benchmark combinations that don't already exist
    for commit in repo.taggedCommits():
        for bm_file_name, bm_file_hash  in bm_files:
            if db.benchmarks.find({"file_hash":bm_file_hash, "commit":commit}).count() < 1 :
                bm_todo[commit].append((bm_file_name, bm_file_hash))
                db.benchmarks.delete_many({"file":bm_file_name, "commit":commit})
    
    return bm_todo, db, db_proc

def benchmark(bm_todo, dirs, db):
    """docstring for benchmark"""
    procs = []
    
    # Run the selected BMs    
    for commit in bm_todo.keys():
        if bm_todo[commit] == []:
            print "Commit %s is up to date" %(commit)
            continue
            
        print "Benchmarking commit %s " % (commit)
        
        # Create an environment to test this commit in 
        env = Environment(dirs['env'], [])
        
        for bm_file_name, bm_file_hash in bm_todo[commit]:
            print "Running BMs in %s " % (bm_file_name)
            
            # Spawn a subprocess to run a set of benchmarks in
            procs.append(env.run([dirs['script'], path.join(dirs['benchmarks'], bm_file_name), commit], cwd=dirs['benchmarks']))
            proc = procs[-1]
            stdoutdata, stderrdata = proc.communicate()
            
            if proc.returncode != 0:
                raise Exception("Failed running benchmark %s" % bm_file_name)
            for line in stdoutdata.split("\n"):
                if line is not '':
                    db.benchmarks.insert(json.loads(line))    
                    print line 
    return procs
    
    
def db_start(db_dir):  
    db_process = Popen(["mongod", "--dbpath", db_dir, "--logpath", path.join(db_dir, "db.log")])        
    sleep(5)
    try:
        conn=pymongo.MongoClient()
    except pymongo.errors.ConnectionFailure, e:
       print "Could not connect to MongoDB: %s" % e   
     
    return conn.db, db_process 