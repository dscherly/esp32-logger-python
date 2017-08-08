import socket
import struct
import time
import datetime
import numpy as np
import scipy.signal

LENGTH_RAW_DATA = 10
LENGTH_CALIBRATED_DATA = 3
DATA_LENGTH = 16
START_BYTE = 83
CRC_BYTE = DATA_LENGTH-2
END_BYTE = 69
MAX_ARRAY_LEN = 100
INIT_BUFFER = 60
SAMPLE_TIME = 0.016666666666667
SENSORBIT0 = 0x01
SENSORBIT1 = 0x02
SENSORBIT2 = 0x04
SENSORBIT3 = 0x08

class Sensor:
    def __init__(self):
    #def __init__(self, node, counter, adc0, adc1, adc2, adc3, crc): #to instantiate with values
        self.len = 0    
        self.node = 0
        self.counter = 0
        self.adc0 = 0
        self.adc1 = 0
        self.adc2 = 0
        self.adc3 = 0
        self.crc = 0
        self.ts = 0
        self.missedPackets = 0
        self.x = np.empty([1,0])
        self.y_ts = np.empty([1,0])
        self.y_adc0 = np.empty([1,0])
        self.y_adc1 = np.empty([1,0])
        self.y_adc2 = np.empty([1,0])
        self.y_adc3 = np.empty([1,0])
        self.sensordata = 0 
        self.tmp = 0
        self.globalcounter = 0
        self.s0 = False

    
    def processCalibratedData(self, data, timestamp):
        self.ts = timestamp
        self.globalcounter += 1
        self.tmp = struct.unpack('<cccccc',data)
        self.len = self.tmp[1]
        self.node = self.tmp[2]
        self.counter = ord(self.tmp[3])
        self.sensordata = ord(self.tmp[4])
        self.crc = self.tmp[5]
        
        self.adc0 = 1 if (self.sensordata & SENSORBIT0) > 0 else 0
        self.adc1 = 1 if (self.sensordata & SENSORBIT1) > 0 else 0
        self.adc2 = 1 if (self.sensordata & SENSORBIT2) > 0 else 0
        self.adc3 = 1 if (self.sensordata & SENSORBIT3) > 0 else 0
        
        self.processRecvData()
        
    def processRawData(self, data, timestamp):
        self.ts = timestamp
        self.globalcounter += 1
        self.tmp = struct.unpack('<ccccHHHHc',data)
        self.len = self.tmp[1]
        self.node = self.tmp[2]
        self.counter = ord(self.tmp[3])
        self.adc2 = self.tmp[4]
        self.adc3 = self.tmp[5]
        self.adc0 = self.tmp[6]
        self.adc1 = self.tmp[7]
        self.crc = self.tmp[8]    
        self.processRecvData()

    def processRecvData(self):
        self.x = np.append(self.x,np.array([self.globalcounter]))
        self.y_ts = np.append(self.y_ts,np.array([self.ts]))
        self.y_adc0 = np.append(self.y_adc0,np.array([self.adc0]))
        self.y_adc1 = np.append(self.y_adc1,np.array([self.adc1]))
        self.y_adc2 = np.append(self.y_adc2,np.array([self.adc2]))
        self.y_adc3 = np.append(self.y_adc3,np.array([self.adc3]))
        
        if len(self.x) > 2 and (self.x[-1] - self.x[-2]) > 1:
            self.missedPackets += self.x[-1] - self.x[-2] - 1
        
        while len(self.x) > MAX_ARRAY_LEN:
            self.x = np.delete(self.x, 0, 0)
            self.y_ts = np.delete(self.y_ts, 0, 0)
            self.y_adc0 = np.delete(self.y_adc0, 0, 0)
            self.y_adc1 = np.delete(self.y_adc1, 0, 0)
            self.y_adc2 = np.delete(self.y_adc2, 0, 0)
            self.y_adc3 = np.delete(self.y_adc3, 0, 0)
       
    def printSensor(self):
        print(datetime.datetime.fromtimestamp(self.ts), self.node, self.counter, 
              self.adc0, self.adc1, self.adc2, self.adc3, self.crc)

def calculate_crc(data):
    out = data[2] ^ data[1]
    for i in range(3,CRC_BYTE):
        out = data[i] ^ out
    return out
    
    
def parseData(sensor, data, index, timestamp):
    try:
        if data[0] != START_BYTE:
            raise Exception 
        
        if data[1] == LENGTH_RAW_DATA and len(data) == (LENGTH_RAW_DATA + 3):
            sensor.processRawData( data, timestamp )
        elif data[1] == LENGTH_CALIBRATED_DATA and len(data) == (LENGTH_CALIBRATED_DATA + 3):
            sensor.processCalibratedData( data, timestamp )
        else:
            raise Exception
        
    except:
        return
