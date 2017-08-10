# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 12:40:32 2017

@author: scey
"""

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
remoteAddr = "192.168.0.100"
remoteport = 14551
localport = 14550

sock.connect((remoteAddr,remoteport))

str = (0xA5,0x0A,0x04,0x01,0,0,0,0,0,0,0,0xB2)
msg = bytearray(str)
sock.send(msg)