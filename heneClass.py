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
        self.counter = 0
        self.syncswitch = 0
        self.data0 = 0
        self.data1 = 0
        self.data2 = 0
        self.data3 = 0
        self.data4 = 0
        self.data5 = 0
        self.data6 = 0
        self.data7 = 0
        self.data8 = 0
        self.data9 = 0
        self.data10 = 0
        self.crc = 0
        self.ts = 0
        self.init_counter = 0
        self.missedPackets = 0
        self.mean_drift = 0
        self.x = np.empty([1,0])
        self.y_ts = np.empty([1,0])
        self.y_deltats = np.empty([1,0])
        self.y_deltats_filt = np.empty([1,0])
        self.y_data0 = np.empty([1,0])
        self.y_data1 = np.empty([1,0])
        self.y_data2 = np.empty([1,0])
        self.y_data3 = np.empty([1,0])
        self.y_data4 = np.empty([1,0])
        self.y_data5 = np.empty([1,0])
        self.y_data6 = np.empty([1,0])
        self.y_data7 = np.empty([1,0])
        self.y_data8 = np.empty([1,0])
        self.y_data9 = np.empty([1,0])
        self.y_data10 = np.empty([1,0])
        self.time_ref = np.empty([1,0]) 
        self.tmp = 0
        
    def clear(self):
        self.counter = 0
        self.syncswitch = 0
        self.data0 = 0
        self.data1 = 0
        self.data2 = 0
        self.data3 = 0
        self.data4 = 0
        self.data5 = 0
        self.data6 = 0
        self.data7 = 0
        self.data8 = 0
        self.data9 = 0
        self.data10 = 0
        self.crc = 0
        self.ts = 0
        self.init_counter = 0
        self.missedPackets = 0
        self.mean_drift = 0
        self.x = np.empty([1,0])
        self.y_ts = np.empty([1,0])
        self.y_deltats = np.empty([1,0])
        self.y_deltats_filt = np.empty([1,0])
        self.y_data0 = np.empty([1,0])
        self.y_data1 = np.empty([1,0])
        self.y_data2 = np.empty([1,0])
        self.y_data3 = np.empty([1,0])
        self.y_data4 = np.empty([1,0])
        self.y_data5 = np.empty([1,0])
        self.y_data6 = np.empty([1,0])
        self.y_data7 = np.empty([1,0])
        self.y_data8 = np.empty([1,0])
        self.y_data9 = np.empty([1,0])
        self.y_data10 = np.empty([1,0])
        self.time_ref = np.empty([1,0]) 
        self.tmp = 0
              
    def unpack(self, data, timestamp):
#        if len(data) != DATA_LENGTH:
#            raise Exception
        #wait some time for input to steady before storing data
        if self.init_counter < INIT_BUFFER:
            self.init_counter += 1
        self.ts = timestamp
#        self.crc = data[48]      
#                        
#        self.tmp = struct.unpack('<cHcfffffffffffcc',data)
#        self.counter = self.tmp[1]
#        self.syncswitch = data[3]
#        self.data0 = self.tmp[3]
#        self.data1 = self.tmp[4]
#        self.data2 = self.tmp[5]
#        self.data3 = self.tmp[6]
#        self.data4 = self.tmp[7]
#        self.data5 = self.tmp[8]
#        self.data6 = self.tmp[9]
#        self.data7 = self.tmp[10]
#        self.data8 = self.tmp[11]
#        self.data9 = self.tmp[12]
#        self.data10 = self.tmp[13]

        self.tmp = struct.unpack('<cHccccccccccccc',data)
        self.counter = self.tmp[1]
        
    def addXY(self):
        #keep a counter of real time according to the pc in timeref
        if self.init_counter == INIT_BUFFER:    
            self.time_ref = np.append(self.time_ref, self.ts)
            self.init_counter += 1
        elif self.init_counter > INIT_BUFFER:
            self.time_ref = np.append(self.time_ref, np.array([(self.counter - self.x[-1])*SAMPLE_TIME + self.time_ref[-1]]))

        if self.init_counter >= INIT_BUFFER:
            self.x = np.append(self.x,np.array([self.counter]))
            self.y_ts = np.append(self.y_ts,np.array([self.ts]))
#            self.y_data0 = np.append(self.y_data0,np.array([self.data0]))
#            self.y_data1 = np.append(self.y_data1,np.array([self.data1]))
#            self.y_data2 = np.append(self.y_data2,np.array([self.data2]))
#            self.y_data3 = np.append(self.y_data3,np.array([self.data3]))
#            self.y_data4 = np.append(self.y_data4,np.array([self.data4]))
#            self.y_data5 = np.append(self.y_data5,np.array([self.data5]))
#            self.y_data6 = np.append(self.y_data6,np.array([self.data6]))
#            self.y_data7 = np.append(self.y_data7,np.array([self.data7]))
#            self.y_data8 = np.append(self.y_data8,np.array([self.data8]))
#            self.y_data9 = np.append(self.y_data9,np.array([self.data9]))
#            self.y_data10 = np.append(self.y_data10,np.array([self.data10]))

            #append the time difference between the time the packet should have been received and when it was received
            self.y_deltats = np.append(self.y_deltats, np.array([(self.y_ts[-1]-self.time_ref[-1])]))
            
            if len(self.x) > 2 and (self.x[-1] - self.x[-2]) > 1:
                self.missedPackets += self.x[-1] - self.x[-2] - 1
            #filter the deltats values and append to filt_deltats
            self.y_deltats_filt = scipy.signal.medfilt(self.y_deltats)
            
            #calculate the mean of the drift. this can then be subtracted
            #self.mean_drift = np.mean(self.y_deltats_filt)
        
        while len(self.x) > MAX_ARRAY_LEN:
            self.x = np.delete(self.x, 0, 0)
            self.y_ts = np.delete(self.y_ts, 0, 0)
#            self.y_data0 = np.delete(self.y_data0, 0, 0)
#            self.y_data1 = np.delete(self.y_data1, 0, 0)
#            self.y_data2 = np.delete(self.y_data2, 0, 0)
#            self.y_data3 = np.delete(self.y_data3, 0, 0)
#            self.y_data4 = np.delete(self.y_data4, 0, 0)
#            self.y_data5 = np.delete(self.y_data5, 0, 0)
#            self.y_data6 = np.delete(self.y_data6, 0, 0)
#            self.y_data7 = np.delete(self.y_data7, 0, 0)
#            self.y_data8 = np.delete(self.y_data8, 0, 0)
#            self.y_data9 = np.delete(self.y_data9, 0, 0)
#            self.y_data10 = np.delete(self.y_data10, 0, 0)
            self.time_ref = np.delete(self.time_ref, 0, 0)
            self.y_deltats = np.delete(self.y_deltats, 0, 0)
            self.y_deltats_filt = np.delete(self.y_deltats_filt, 0, 0)
       
    def printData(self):
        print(datetime.datetime.fromtimestamp(self.ts), self.counter, self.syncswitch,
              self.data0, self.data1, self.data2, self.data3, self.data4, self.data5, 
              self.data6, self.data7, self.data8, self.data9, self.data10, self.crc)

def calculate_crc(data):
    out = data[2] ^ data[1]
    for i in range(3,CRC_BYTE):
        out = data[i] ^ out
    return out
    
    
def parseData(sensor, data, index, timestamp):
    try:
#        if len(data) != DATA_LENGTH:
#            raise Exception 
#        elif data[0] != START_BYTE:
#            raise Exception 
#        elif data[DATA_LENGTH-1] != END_BYTE:
#            raise Exception 
        
#        #calculate CRC to check data integrity
#        calculated_crc = calculate_crc(data)
#        if calculated_crc != data[CRC_BYTE]:
#            #print("Recv CRC:", data[DATA_LENGTH-2],"Calc CRC: ", calculated_crc)
#            raise Exception        
              
        #unpack data into the buffer
        sensor.unpack(data, timestamp)

    except:
        return
