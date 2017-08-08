# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 09:33:45 2017

@author: scey
"""
#from sys import argv
import struct
import re

#use argument as filename
#script, filename = argv

#parse logfile saved by xosoft app
fname = "file"

with open(fname) as f:
    content = f.readlines()
    
content = [x.strip('\n') for x in content]
print(content[2])

p = re.compile('\\\\x([a-z0-9][a-z0-9])')
m = p.findall(content[2])
print("match = :", m)