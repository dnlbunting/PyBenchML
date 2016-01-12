#!/usr/bin/env python
from subprocess import Popen, PIPE
import os, re
from json import loads
from .core import COMMIT_SYM, CONFIG_NAME

class GitException(Exception):
    def __init__(self, call_args, ret, stdout, stderr, *args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
        self.ret = ret
        self.stdout = stdout
        self.stderr = stderr
        self.call_args = call_args
    def __str__(self):
        return "GitException(%s, %s, %s, %s)" % (self.call_args, self.ret, self.stdout, self.stderr)
                
def gitCall(args, cwd=None, verbose=False):
    '''Handles the external call to Git
    by creating a subprocess with git + args optionally after cd'ing into cwd '''
    
    ret, stdoutdata, stderrdata = None, None, None
    args = [args] if isinstance(args, basestring) else args
    
    if verbose:
        print "---- Call to git -----"
        print "args: %s" % (args)
        print "stdout: %s" % (stdoutdata)
        print "stderr: %s" % (stderrdata)
         
    try:
        p = Popen(["git"] + args, cwd=cwd, stdout=PIPE, stderr=PIPE)
        stdoutdata, stderrdata = p.communicate()
        ret = p.returncode
        
        if ret != 0:
            raise(GitException(args, ret, stdoutdata, stderrdata))
    
    except :            
        raise(GitException(args, ret, stdoutdata, stderrdata))
        
    return stdoutdata
    
def isRepoBase(dir):
    """Return true if dir is the base of the git repo, ie 
        git status returns 0 in dir and not in the parents of dir"""
    
    try:
        gitCall("status", cwd=dir)
        isdir = True        
    except GitException, e:
        isdir = False
   
    try:    
        gitCall("status", cwd=os.path.join(dir + "/../"))
        isdirpar = True        
    except GitException, e:
        isdirpar = False
            
    return isdir and not isdirpar
    


class LFSRepo(object):
    """A local file system clone of a git repository"""
    def __init__(self, base_dir, origin_repo):
        super(LFSRepo, self).__init__()
        self.base_dir = base_dir
        self.origin_repo = origin_repo
        
        try:
            gitCall(["clone", self.origin_repo, self.base_dir])
        except GitException, e:
            "Failed cloning repository"
            print e
            
        try:
            with open(os.path.join(self.base_dir, CONFIG_NAME), 'r') as file:
                self.config = json.loads(' '.join([line for line in file]))
        except:
            raise Exception("Filed to locate a config file for the repo")
               
    
    def checkout(self, commit):
        """docstring for checkout"""
        gitCall(["checkout","-f" , commit], cwd=self.base_dir)
        
        
    def taggedCommits(self):
        """Returns a list of commit hashes that contained the benchmarking directive"""
        stdout = gitCall(["log", "--format=oneline", "--grep", COMMIT_SYM], cwd=self.base_dir)
        commit_list = [re.match("^(\S+)", commit).groups()[0] for commit in stdout.split("\n") if re.match("^(\S+)", commit) is not None]
                
        return commit_list
        
    