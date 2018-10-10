# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 08:38:18 2018

@author: hztengkezhen
"""

class A(object):
    @property
    def weight(self):
        print 'hello'
        return 10

a = A()
print a.weight
print a.weight