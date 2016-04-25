#!/usr/bin/env python

from bottle import Bottle, run, static_file, post, request
import sys, os, json
app = Bottle()

html_dir = os.path.join(os.path.dirname(__file__), "html")
scripts_dir = os.path.join(os.path.dirname(__file__), "html/scripts")

db = None


################################################
#           Static resources                   #
################################################

@app.route('/scripts/<filename>')
def scripts(filename):
    return static_file(os.path.join("scripts/", filename), root=html_dir)  

@app.route('/css/<filename>')
def css(filename):
    return static_file(os.path.join("css/", filename), root=html_dir)
    

################################################
#               Database API                    #
################################################

@app.route('/commits/<commit>')
def get_commit(commit):
    print "Fetching commit %s" %(commit)
    global db
    doc_list = [x for x in db.benchmarks.find({"commit":commit}, projection={'_id': False})]
    
    if doc_list is None:
        return json.dumps({"commit":commit, "value" : []})
    else:
        return json.dumps({"commit":commit, "value" : doc_list})

@app.route("/commitviewinit")
def get_commitList():
    """docstring for get_commitList"""
    
    return json.dumps({"commitList":[x for x in db.benchmarks.distinct("commit")],
                        "fileList":[x for x in db.benchmarks.distinct("file")]})        


'''Example query:
    
    {"commit":[adfa, dasfsdf, fgdffg],
    "file":"file1"}    
    
'''


@app.route("/dbquery", method="POST")
def dbquery():
    """docstring for get_commitList"""
    global db
    print request.json
    query = buildQuery(request.json)
    print query
    doc_list = [x for x in db.benchmarks.find(query, projection={'_id': False})]    
    return json.dumps(doc_list) 

def buildQuery(filters):
    query = {"$and":[]}
    for k,v in filters.items():
        query["$and"]+= [{"$or":[{k:e} for e in v]}]
            
    return query    

def buildQuery3(filters):
    query = {}
    for k,v in filters.items():
        
        if type(v) == list:
            # Turn a list into an or query
            q = [{k:x} for x in v]
            try:
                query["$or"]+= q
            except KeyError:
                query["$or"] = q
        
        elif type(v) == str or len(v) == 1:
            query[k] = [v]
        else:
            raise ValueError
            
    return query
################################################
#                   Pages                      #
################################################

@app.route('/')
def index():
    return static_file('index.html', root=html_dir)  

@app.route('/commitView')
def commits():
    return static_file('commits.html', root=html_dir)  
    
  
    


    
    
def server_main(args, config, dirs, db_):
    print "Starting websever"
    global db
    db = db_
    run(app, host='localhost', port=5050)
    