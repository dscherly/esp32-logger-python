# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 14:46:03 2017

@author: scey
"""

import sys
import socket
import time
import datetime
import struct
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import sensorClass
import heneClass2
import numpy as np

np.set_printoptions(threshold=np.nan,linewidth=np.nan)

LEFT = 0
RIGHT = 1
HENEBOARD = 2

UDP_HENEBOARD = "192.168.0.101"    #local ip address
UDP_HENEPORT = 14550    #local UDP port
UDP_IP0 = "192.168.0.101"
UDP_PORT0 = 16501
UDP_IP1 = "192.168.0.101"
UDP_PORT1 = 16511
        
class xosoft(QtGui.QWidget):
    def __init__(self):
        super(xosoft, self).__init__()
        self.init_ui()
        self.qt_connections()
        self.connect_sockets()
        self.logstate = False;
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0.1)
        
    def init_ui(self):
        self.setWindowTitle('Xosoft')
        grid = QtGui.QGridLayout()
        grid.setColumnMinimumWidth(2,500)
        self.setLayout(grid)
        
        pg.setConfigOptions(antialias=True)
        self.setGeometry(200, 100, 600, 800)
        
        #labels for the rows
        self.label_hene = QtGui.QLabel("Hene board")
        grid.addWidget(self.label_hene, 1,1)
        self.label_left = QtGui.QLabel("Left foot")
        grid.addWidget(self.label_left, 2,1)
        self.label_right = QtGui.QLabel("Right foot")
        grid.addWidget(self.label_right, 3,1)

        #start and stop logging buttons
        self.logbutton = QtGui.QPushButton("Start logging")
        grid.addWidget(self.logbutton,4,2)
        
        #send command to nucleo to start sending data
        self.imubutton = QtGui.QPushButton("IMU start")
        grid.addWidget(self.imubutton,5,2)
        
        #data plot for hene board
        self.plotwidget_hene = pg.PlotWidget()
        self.plotwidget_hene.setLabel('left','ADC')
        self.plotwidget_hene.setBackground('w')
        grid.addWidget(self.plotwidget_hene,1,2)
        self.plotcurve_hene0 = pg.PlotCurveItem()
        self.plotcurve_hene0.setData(pen='k')
        self.plotwidget_hene.addItem(self.plotcurve_hene0)
        self.plotcurve_hene1 = pg.PlotCurveItem()
        self.plotcurve_hene1.setData(pen='r')
        self.plotwidget_hene.addItem(self.plotcurve_hene1)
        self.plotcurve_hene2 = pg.PlotCurveItem()
        self.plotcurve_hene2.setData(pen='g')
        self.plotwidget_hene.addItem(self.plotcurve_hene2)
        self.plotcurve_hene3 = pg.PlotCurveItem()
        self.plotcurve_hene3.setData(pen='b')
        self.plotwidget_hene.addItem(self.plotcurve_hene3)
        self.plotcurve_hene4 = pg.PlotCurveItem()
        self.plotcurve_hene4.setData(pen='c')
        self.plotwidget_hene.addItem(self.plotcurve_hene4)
        self.plotcurve_hene5 = pg.PlotCurveItem()
        self.plotcurve_hene5.setData(pen='m')
        self.plotwidget_hene.addItem(self.plotcurve_hene5)
        self.plotcurve_hene6 = pg.PlotCurveItem()
        self.plotcurve_hene6.setData(pen='y')
        self.plotwidget_hene.addItem(self.plotcurve_hene6)
        self.plotcurve_hene7 = pg.PlotCurveItem()
        self.plotcurve_hene7.setData(pen='k')
        self.plotwidget_hene.addItem(self.plotcurve_hene7)
        self.plotcurve_hene8 = pg.PlotCurveItem()
        self.plotcurve_hene8.setData(pen='r')
        self.plotwidget_hene.addItem(self.plotcurve_hene8)
        self.plotcurve_hene9 = pg.PlotCurveItem()
        self.plotcurve_hene9.setData(pen='g')
        self.plotwidget_hene.addItem(self.plotcurve_hene9)
        self.plotcurve_hene10 = pg.PlotCurveItem()
        self.plotcurve_hene10.setData(pen='b')
        self.plotwidget_hene.addItem(self.plotcurve_hene10)
        
        #data plot for left foot
        self.plotwidget_left = pg.PlotWidget()
        self.plotwidget_left.setLabel('left','ADC')
#        self.plotwidget_left.setYRange(0,4100)
        self.plotwidget_left.setBackground('w')
        grid.addWidget(self.plotwidget_left,2,2)
        self.plotcurve_left0 = pg.PlotCurveItem()
        self.plotcurve_left0.setData(pen='k')
        self.plotwidget_left.addItem(self.plotcurve_left0)
        self.plotcurve_left1 = pg.PlotCurveItem()
        self.plotcurve_left1.setData(pen='r')
        self.plotwidget_left.addItem(self.plotcurve_left1)
        self.plotcurve_left2 = pg.PlotCurveItem()
        self.plotcurve_left2.setData(pen='g')
        self.plotwidget_left.addItem(self.plotcurve_left2)
        self.plotcurve_left3 = pg.PlotCurveItem()
        self.plotcurve_left3.setData(pen='b')
        self.plotwidget_left.addItem(self.plotcurve_left3)
        
        #data plot for right foot
        self.plotwidget_right = pg.PlotWidget()
        self.plotwidget_right.setLabel('left','ADC')
#        self.plotwidget_right.setYRange(0,4100)
        self.plotwidget_right.setBackground('w')
        grid.addWidget(self.plotwidget_right,3,2)
        self.plotcurve_right0 = pg.PlotCurveItem()
        self.plotcurve_right0.setData(pen='k')
        self.plotwidget_right.addItem(self.plotcurve_right0)
        self.plotcurve_right1 = pg.PlotCurveItem()
        self.plotcurve_right1.setData(pen='r')
        self.plotwidget_right.addItem(self.plotcurve_right1)
        self.plotcurve_right2 = pg.PlotCurveItem()
        self.plotcurve_right2.setData(pen='g')
        self.plotwidget_right.addItem(self.plotcurve_right2)
        self.plotcurve_right3 = pg.PlotCurveItem()
        self.plotcurve_right3.setData(pen='b')
        self.plotwidget_right.addItem(self.plotcurve_right3)
        
        #checkboxes to show or hide adc plots
        self.checkbox_hene = QtGui.QCheckBox()
        self.checkbox_hene.setChecked(True)
        grid.addWidget(self.checkbox_hene,1,3)
        self.showHene = True
        self.checkbox_left = QtGui.QCheckBox()
        self.checkbox_left.setChecked(True)
        grid.addWidget(self.checkbox_left,2,3)
        self.showLeft = True
        self.checkbox_right = QtGui.QCheckBox()
        self.checkbox_right.setChecked(True)
        grid.addWidget(self.checkbox_right,3,3)
        self.showRight = True
                
        self.heneMissedPackets = QtGui.QLabel("0")
        grid.addWidget(self.heneMissedPackets,1,4)
        self.leftMissedPackets = QtGui.QLabel("0")
        grid.addWidget(self.leftMissedPackets,2,4)
        self.rightMissedPackets = QtGui.QLabel("0")
        grid.addWidget(self.rightMissedPackets,3,4)

        self.show()
        
    def qt_connections(self):
        self.logbutton.clicked.connect(self.on_logbutton_clicked)
        self.imubutton.clicked.connect(self.on_imubutton_clicked)
        self.checkbox_hene.clicked.connect(self.on_checkbox_hene_clicked)
        self.checkbox_left.clicked.connect(self.on_checkbox_left_clicked)
        self.checkbox_right.clicked.connect(self.on_checkbox_right_clicked)

    def connect_sockets(self):
        self.sensor0 = sensorClass.Sensor()
        self.sensor1 = sensorClass.Sensor()
        self.heneboard = heneClass2.Heneboard()
        
        #left foot socket
        self.sock0 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock0.bind((UDP_IP0, UDP_PORT0))
            self.sock0.setblocking(0)
            self.sock0.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            print("socket",self.sock0,"bind fail")
            self.close()
            sys.exit()
        
        #right foot socket
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock1.bind((UDP_IP1, UDP_PORT1))
            self.sock1.setblocking(0)   
            self.sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            print("socket",self.sock1,"bind fail")
            self.close()
            sys.exit()
            
        #heneboard socket
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock2.bind((UDP_HENEBOARD, UDP_HENEPORT))
            self.sock2.setblocking(0)
            self.sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error:
            print("socket",self.sock2,"bind fail")
            self.close()
            sys.exit()
            
        self.socketlist = [self.sock0, self.sock1, self.sock2]
        
    def update(self):
        #try to read from each socket
        for idx, sock in enumerate(self.socketlist):
            try:
                data, addr = sock.recvfrom(1024)
                #left foot
                if idx == LEFT:
                    sensorClass.parseData(self.sensor0, data, idx, time.time())
                    if self.showLeft and self.sensor0.x.size > 0:
                        self.plotcurve_left0.setData(self.sensor0.x, self.sensor0.y_adc0)
                        self.plotcurve_left1.setData(self.sensor0.x, self.sensor0.y_adc1)
                        self.plotcurve_left2.setData(self.sensor0.x, self.sensor0.y_adc2)
                        self.plotcurve_left3.setData(self.sensor0.x, self.sensor0.y_adc3)
                    self.leftMissedPackets.setText(str(self.sensor0.missedPackets))
                    
                    if self.logstate:
                        print('left',
                              self.sensor0.counter,
                              self.sensor0.ts,
                              self.sensor0.adc0,
                              self.sensor0.adc1,
                              self.sensor0.adc2,
                              self.sensor0.adc3,
                              file=self.f)

                #right foot                
                elif idx == RIGHT:
                    sensorClass.parseData(self.sensor1, data, idx, time.time())
                    if self.showRight and self.sensor1.x.size > 0:
                        self.plotcurve_right0.setData(self.sensor1.x, self.sensor1.y_adc0)
                        self.plotcurve_right1.setData(self.sensor1.x, self.sensor1.y_adc1)
                        self.plotcurve_right2.setData(self.sensor1.x, self.sensor1.y_adc2)
                        self.plotcurve_right3.setData(self.sensor1.x, self.sensor1.y_adc3)
                    self.rightMissedPackets.setText(str(self.sensor1.missedPackets))
                    
                    if self.logstate:
                        print('right',
                              self.sensor1.counter,
                              self.sensor1.ts,
                              self.sensor1.adc0,
                              self.sensor1.adc1,
                              self.sensor1.adc2,
                              self.sensor1.adc3,
                              file=self.f)
                        
                elif idx == HENEBOARD:
                    #obtain serial data from nucleo board, this needs to go somewhere else
                    #print("received data",len(data),"bytes")
                    d = data
                    while True:
                        if len(d) < 14:
                            break
                        packet = d[:14]
                        d = d[14:]
            
                        #unpack data into the buffer
                        try:
                            tmp = struct.unpack('<cccccffc',packet)
                            print(ord(tmp[0]),ord(tmp[1]),ord(tmp[2]),ord(tmp[3]),ord(tmp[4]),tmp[5],tmp[6],ord(tmp[7]))

                            if self.logstate:
                                print('imu',
                                      ord(tmp[0]),
                                      ord(tmp[1]),
                                      ord(tmp[2]),
                                      ord(tmp[3]),
                                      ord(tmp[4]),
                                      tmp[5],
                                      tmp[6],
                                      ord(tmp[7]),
                                      file=self.f)
                        except:
                            pass

                    #commented out to test CAN data from CSIC Nucleo board
                    #                    self.parseData(self.heneboard, data, idx, time.time())
                    #                    
                    #                    if self.showHene and self.heneboard.data0.size > 0:
                    #                        self.plotcurve_hene0.setData(self.heneboard.ts0, self.heneboard.data0)
                    #                    if self.showHene and self.heneboard.data1.size > 0:
                    #                        self.plotcurve_hene1.setData(self.heneboard.ts1, self.heneboard.data1)
                         

            except socket.error:
                pass
    
        
    def on_logbutton_clicked(self):
        if self.logstate == False:
            self.logbutton.setText("Stop logging")
            self.heneboard.clear()
            
            print ("Logging started")
            self.checkbox_hene.setChecked(False)
            self.checkbox_left.setChecked(False)
            self.checkbox_right.setChecked(False)
            self.showHene = False
            self.showLeft = False
            self.showRight = False

            self.logstate = True

            date = datetime.datetime.today()
            filename = "log_%d%02d%02d_%02d%02d%02d.csv" % (date.year, date.month, date.day, date.hour, date.minute, date.second)
            self.f = open(filename,'w')
            print("Sensor Counter Timestamp ADC0 ADC1 ADC2 ADC3\nChannel Timestamp Value", file=self.f)

        else:
            print ("Logging stopped")

            #save heneboard log data to a file                    
            self.print_data_to_file('Data0',self.heneboard.ts0,self.heneboard.data0)
            self.print_data_to_file('Data1',self.heneboard.ts1,self.heneboard.data1)
            self.print_data_to_file('Data2',self.heneboard.ts2,self.heneboard.data2)
            self.print_data_to_file('Data3',self.heneboard.ts3,self.heneboard.data3)
            self.print_data_to_file('Data4',self.heneboard.ts4,self.heneboard.data4)
            self.print_data_to_file('Data5',self.heneboard.ts5,self.heneboard.data5)
            self.print_data_to_file('Data6',self.heneboard.ts6,self.heneboard.data6)
            self.print_data_to_file('Data7',self.heneboard.ts7,self.heneboard.data7)
            self.print_data_to_file('Data8',self.heneboard.ts8,self.heneboard.data8)
            self.print_data_to_file('Data9',self.heneboard.ts9,self.heneboard.data9)
            self.f.close()
            
            self.heneboard.max_array_length = heneClass2.MAX_ARRAY_LEN
            self.logbutton.setText("Start logging")
            self.logstate = False
            self.checkbox_hene.setChecked(True)
            self.checkbox_left.setChecked(True)
            self.checkbox_right.setChecked(True)
            self.showHene = True
            self.showLeft = True
            self.showRight = True
    
    def on_imubutton_clicked(self):
        com = bytearray.fromhex("a5 01 ff 00 00")
        com[4] = (com[1]^com[2])^com[3]
        print("sending IMU start command:",com[0],com[1],com[2],com[3],com[4])
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send imu udp command")
        
        
    def print_data_to_file(self,str1,ts,data):        
        for i in range(0,(len(data)-1)):
            print(str1,end=" ",file=self.f)
            print(ts[i], end=" ", file=self.f)
            print(data[i], file=self.f)
            
    def on_checkbox_hene_clicked(self):
        if self.checkbox_hene.isChecked():
            self.showHene = True
        else:
            self.showHene = False
            
    def on_checkbox_left_clicked(self):
        if self.checkbox_left.isChecked():
            self.showLeft = True
        else:
            self.showLeft = False
            
    def on_checkbox_right_clicked(self):
        if self.checkbox_right.isChecked():
            self.showRight = True
        else:
            self.showRight = False
            
    def closeEvent(self, event):
        try:
            self.sock0.shutdown(socket.SHUT_RDWR)
            self.sock0.close()
        except:
            pass
        try:
            self.sock1.shutdown(socket.SHUT_RDWR)
            self.sock1.close()
        except:
            pass
        try:
            self.sock2.shutdown(socket.SHUT_RDWR)
            self.sock2.close()
        except:
            pass
        if self.logstate == True:   #stop logging when closed
            self.on_logbutton_clicked()
        print("Window closed -> Sockets shutdown")
        event.accept()

    def parseData(self, sensor, data, index, timestamp):
        try:
            #take 10 bytes at a time
            tmp = data
            while True:
                if len(tmp) < 10:
                    break
                packet = tmp[:10]
                tmp = tmp[10:]
            
                #unpack data into the buffer
                sensor.unpack(packet, timestamp)
    
        except:
            return

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('xosoft')
    ex = xosoft()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
