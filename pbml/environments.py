#!/usr/bin/env python
from subprocess import Popen, PIPE
import os
import hashlib

class Environment(object):
    """docstring for Environment"""
    
    def __init__(self, base_dir, requirements, python='python', site_packages=False, verbose=False):
        super(Environment, self).__init__()
        self.base_dir = os.path.abspath(base_dir)
        self.requirements = requirements
        self.python = python
        hasher = hashlib.sha224()
        
        self._create(verbose=verbose)
        for req in self.requirements:
            self.install(req, verbose=verbose)
            hasher.update(req)
                    
        hasher.update(self.base_dir)
        hasher.update(self.python)    
        self.hash = hasher.digest()
        
    def __hash__(self):
        return self.hash
             
    def _create(self, verbose=False):
            
        try:
            ret, stdoutdata, stderrdata = None, None, None
            p = Popen(["virtualenv", "--python", self.python, self.base_dir], stdout=PIPE, stderr=PIPE)
            stdoutdata, stderrdata = p.communicate()
            ret = p.returncode
            
            if ret != 0:
                raise(Exception("Failed to create virtualenv:\n%s\n%s" % (stdoutdata, stderrdata)))
        
        except :            
            print "Failed to create virtualenv:\n%s\n%s" % (stdoutdata, stderrdata)
            raise 
            
        
        
    def install(self, package, verbose=False):
        
        try:
            ret, stdoutdata, stderrdata = None, None, None
            p = Popen([os.path.join(self.base_dir, "bin/pip"), "install", package], stdout=PIPE, stderr=PIPE)
            stdoutdata, stderrdata = p.communicate()
            ret = p.returncode
           
            if ret != 0:
                raise(Exception("Failed to install package %s:\n%s\n%s" % (package, stdoutdata, stderrdata)))
        
        except :            
                print "Failed to install package %s:\n%s\n%s" % (package, stdoutdata, stderrdata)
                raise
            
    def run(self, args, cwd=None):
        """docstring for run"""
        try:
            ret, stdoutdata, stderrdata = None, None, None
            p = Popen([os.path.join(self.base_dir, "bin/python")]+args, stdout=PIPE, stderr=None, cwd=cwd)
            return p               
        except :            
                print "Failed to call venv python %s" % (args)
                raise