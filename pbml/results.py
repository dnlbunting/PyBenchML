from .utils import filehash
from .run import db_start
from .server import server_main


import os.path as path
import argparse     
import numpy as np

def results_main(args, config, dirs):
    """docstring for main"""
    
    db, db_proc = db_start(dirs['db'])

    if args.output == "print":
        print "Dumping database"
        for x in db.benchmarks.find():
            print x 
            print "\n"

    elif args.output == 'mpl':
        mpl(args, config, dirs, db)

        
    else:
        print "Invalid option"
        
        

def mpl(args, config, dirs, db):
    """docstring for mpl"""
    
    import matplotlib.pyplot as plt
    plt.style.use(u'lab_report')
    
    for commit in db.benchmarks.distinct("commit"):
        plt.figure()
        
        records = [x for x in db.benchmarks.find({"commit":commit})]
        
        N = len(records) 
        bms = [x['benchmark'] for x in records]
        times = [np.mean(x['times']) for x in records]
        times_err = [np.std(x['times']) for x in records]
        
        lefts = np.arange(N) + 0.1
        
        plt.bar(lefts, times, yerr=times_err)
    plt.show()
    
