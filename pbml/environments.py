#!/usr/bin/env python
from subprocess import Popen, PIPE
import os
import hashlib

class Evironment(object):
    """docstring for Evironment"""
    
    def __init__(self, base_dir, requirements, python='python', site_packages=False, verbose=False):
        super(Evironment, self).__init__()
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
           
            if verbose:
                print "---- Call to vitualenv -----"
                print "python: %s" % (self.python)
                print "base_dir: %s" % (self.base_dir)
                print "stdout: %s" % (stdoutdata)
                print "stderr: %s" % (stderrdata)
            
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
            
            if verbose:
                print "---- Call to pip -----"
                print "package: %s" % (package)
                print "stdout: %s" % (stdoutdata)
                print "stderr: %s" % (stderrdata)
           
            if ret != 0:
                raise(Exception("Failed to install package %s:\n%s\n%s" % (package, stdoutdata, stderrdata)))
        
        except :            
                print "Failed to install package %s:\n%s\n%s" % (package, stdoutdata, stderrdata)
                raise
            