# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 15:13:34 2017

@author: scey
"""

import socket
import struct
import time
import datetime
import numpy as np
import scipy.signal


DATA_LENGTH = 50
START_BYTE = 83
CRC_BYTE = DATA_LENGTH-2
END_BYTE = 69
MAX_ARRAY_LEN = 100
INIT_BUFFER = 60
SAMPLE_TIME = 0.008333333333333333

class Heneboard:
    def __init__(self):
        self.ts0 = np.empty([1,0])
        self.ts1 = np.empty([1,0])
        self.ts2 = np.empty([1,0])
        self.ts3 = np.empty([1,0])
        self.ts4 = np.empty([1,0])
        self.ts5 = np.empty([1,0])
        self.ts6 = np.empty([1,0])
        self.ts7 = np.empty([1,0])
        self.ts8 = np.empty([1,0])
        self.ts9 = np.empty([1,0])
        self.data0 = np.empty([1,0])
        self.data1 = np.empty([1,0])
        self.data2 = np.empty([1,0])
        self.data3 = np.empty([1,0])
        self.data4 = np.empty([1,0])
        self.data5 = np.empty([1,0])
        self.data6 = np.empty([1,0])
        self.data7 = np.empty([1,0])
        self.data8 = np.empty([1,0])
        self.data9 = np.empty([1,0])
        self.max_array_length = MAX_ARRAY_LEN
        self.tmp = 0
        
    def clear(self):
        self.ts0 = np.empty([1,0])
        self.ts1 = np.empty([1,0])
        self.ts2 = np.empty([1,0])
        self.ts3 = np.empty([1,0])
        self.ts4 = np.empty([1,0])
        self.ts5 = np.empty([1,0])
        self.ts6 = np.empty([1,0])
        self.ts7 = np.empty([1,0])
        self.ts8 = np.empty([1,0])
        self.ts9 = np.empty([1,0])
        self.data0 = np.empty([1,0])
        self.data1 = np.empty([1,0])
        self.data2 = np.empty([1,0])
        self.data3 = np.empty([1,0])
        self.data4 = np.empty([1,0])
        self.data5 = np.empty([1,0])
        self.data6 = np.empty([1,0])
        self.data7 = np.empty([1,0])
        self.data8 = np.empty([1,0])
        self.data9 = np.empty([1,0])
        self.max_array_length = 100000
        self.tmp = 0
              
    def unpack(self, data, timestamp):
        self.tmp = struct.unpack('>ccccccI',data)
#        print(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9])
        
        n = ord(self.tmp[5]) #sensor number
        if n == 0:
            self.data0 = np.append(self.data0, np.array([self.tmp[6]]))
            self.ts0 = np.append(self.ts0, timestamp)
        if n == 1:
            self.data1 = np.append(self.data1, self.tmp[6])
            self.ts1 = np.append(self.ts1,timestamp)
        if n == 2:
            self.data2 = np.append(self.data2, self.tmp[6])
            self.ts2 = np.append(self.ts2,timestamp)
        if n == 3:
            self.data3 = np.append(self.data3, self.tmp[6])
            self.ts3 = np.append(self.ts3,timestamp)
        if n == 4:
            self.data4 = np.append(self.data4, self.tmp[6])
            self.ts4 = np.append(self.ts4,timestamp)
        if n == 5:
            self.data5 = np.append(self.data5, self.tmp[6])
            self.ts5 = np.append(self.ts5,timestamp)
        if n == 6:
            self.data6 = np.append(self.data6, self.tmp[6])
            self.ts6 = np.append(self.ts6,timestamp)
        if n == 7:
            self.data7 = np.append(self.data7, self.tmp[6])
            self.ts7 = np.append(self.ts7,timestamp)
        if n == 8:
            self.data8 = np.append(self.data8, self.tmp[6])
            self.ts8 = np.append(self.ts8,timestamp)
        if n == 9:
            self.data9 = np.append(self.data9, self.tmp[6])
            self.ts9 = np.append(self.ts9,timestamp)
            
        
        while len(self.data0) > self.max_array_length:
                self.data0 = np.delete(self.data0, 0, 0)
        while len(self.data1) > self.max_array_length:
                self.data1 = np.delete(self.data1, 0, 0)
        while len(self.data2) > self.max_array_length:
                self.data2 = np.delete(self.data2, 0, 0)
        while len(self.data3) > self.max_array_length:
                self.data3 = np.delete(self.data3, 0, 0)
        while len(self.data4) > self.max_array_length:
                self.data4 = np.delete(self.data4, 0, 0)
        while len(self.data5) > self.max_array_length:
                self.data5 = np.delete(self.data5, 0, 0)
        while len(self.data6) > self.max_array_length:
                self.data6 = np.delete(self.data6, 0, 0)
        while len(self.data7) > self.max_array_length:
                self.data7 = np.delete(self.data7, 0, 0)
        while len(self.data8) > self.max_array_length:
                self.data8 = np.delete(self.data8, 0, 0)
        while len(self.data9) > self.max_array_length:
                self.data9 = np.delete(self.data9, 0, 0)
        
        while len(self.ts0) > self.max_array_length:
            self.ts0 = np.delete(self.ts0, 0, 0)
        while len(self.ts1) > self.max_array_length:
            self.ts1 = np.delete(self.ts1, 0, 0)
        while len(self.ts2) > self.max_array_length:
            self.ts2 = np.delete(self.ts2, 0, 0)
        while len(self.ts3) > self.max_array_length:
            self.ts3 = np.delete(self.ts3, 0, 0)
        while len(self.ts4) > self.max_array_length:
            self.ts4 = np.delete(self.ts4, 0, 0)
        while len(self.ts5) > self.max_array_length:
            self.ts5 = np.delete(self.ts5, 0, 0)
        while len(self.ts6) > self.max_array_length:
            self.ts6 = np.delete(self.ts6, 0, 0)
        while len(self.ts7) > self.max_array_length:
            self.ts7 = np.delete(self.ts7, 0, 0)
        while len(self.ts8) > self.max_array_length:
            self.ts8 = np.delete(self.ts8, 0, 0)
        while len(self.ts9) > self.max_array_length:
            self.ts9 = np.delete(self.ts9, 0, 0)

#    def check_array_length(self,ts,data):        
#        while len(ts) > self.max_array_length:
#            ts = np.delete(ts, 0, 0)
#            print("length",len(ts))
#        while len(data) > self.max_array_length:
#            data = np.delete(data, 0, 0)
            
def calculate_crc(data):
    out = data[2] ^ data[1]
    for i in range(3,CRC_BYTE):
        out = data[i] ^ out
    return out
    

