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
import requests

np.set_printoptions(threshold=np.nan,linewidth=np.nan)

LEFT = 0
RIGHT = 1
HENEBOARD = 2

CAN_MSG = 255
IMU_1_MSG = 11
IMU_2_MSG = 12
IMU_3_MSG = 13
IMU_4_MSG = 14
FOOT_R = 5
FOOT_L = 6

UDP_HENEBOARD = "192.168.0.101"    #local ip address
UDP_HENEPORT = 14550    #local UDP port
UDP_IP0 = "192.168.0.101"
UDP_PORT0 = 16501
UDP_IP1 = "192.168.0.101"
UDP_PORT1 = 16511
        
START_BYTE = 165
START_BYTE_FOOT = 83

calibrate_flag = False
calibrate_success = False
sensors_R = [0,0,0,0]
sensors_L = [0,0,0,0]
thresholds_r = [500,500,500,500]
thresholds_l = [500,500,500,500]
r_s0 = np.empty([1,0])
r_s1 = np.empty([1,0])
r_s2 = np.empty([1,0])
r_s3 = np.empty([1,0])
l_s0 = np.empty([1,0])
l_s1 = np.empty([1,0])
l_s2 = np.empty([1,0])
l_s3 = np.empty([1,0])

max_R = [0,0,0,0]
min_R = [65535,65535,65535,65535]

#functions for the sensor calibration dialog
class Calibrate_dialog(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Calibrate_dialog, self).__init__(parent)
        self.init_ui()
        self.qt_connections()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)
        
    def init_ui(self):
        self.setWindowTitle('Sensor calibration')
        self.setGeometry(450, 100, 300, 400)
        
        #mainwindow needs a widget to hold contents
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        
        #add a grid to the main window widget
        grid = QtGui.QGridLayout()
        #grid.setColumnMinimumWidth(0,600)
        grid.setRowMinimumHeight(0,170)
        grid.setRowMinimumHeight(1,170)
        grid.setRowMinimumHeight(2,170)
        grid.setRowMinimumHeight(3,170)
        self.widget.setLayout(grid)
        
        #buttons
        self.resetbutton = QtGui.QPushButton("Reset plots")
        grid.addWidget(self.resetbutton,5,0,1,1)
        
        self.button = QtGui.QPushButton("Set thresholds")
        grid.addWidget(self.button,6,0,1,1)     
        
        self.radiobutton_r = QtGui.QRadioButton()
        self.radiobutton_r.setChecked(True)
        grid.addWidget(self.radiobutton_r,5,2,1,1)     
        
        self.radiobutton_l = QtGui.QRadioButton()
        grid.addWidget(self.radiobutton_l,6,2,1,1)   
        
        #labels
        self.label1 = QtGui.QLabel('Heel')
        self.label2 = QtGui.QLabel('Outside')
        self.label3 = QtGui.QLabel('Inside')
        self.label4 = QtGui.QLabel('Toe')
        self.label5 = QtGui.QLabel('Right')
        self.label6 = QtGui.QLabel('Left')
        self.label7 = QtGui.QLabel('')
        grid.addWidget(self.label1,4,3,1,1)
        grid.addWidget(self.label2,4,4,1,1)
        grid.addWidget(self.label3,4,5,1,1)
        grid.addWidget(self.label4,4,6,1,1)
        grid.addWidget(self.label5,5,1,1,1)
        grid.addWidget(self.label6,6,1,1,1)
        grid.addWidget(self.label7,7,0,1,6)
        
        #input fields for individual threshold values
        self.t_r0 = QtGui.QLabel()
        self.t_r1 = QtGui.QLabel()
        self.t_r2 = QtGui.QLabel()
        self.t_r3 = QtGui.QLabel()
        self.t_r0.setText(str(thresholds_r[0]))
        self.t_r1.setText(str(thresholds_r[1]))
        self.t_r2.setText(str(thresholds_r[2]))
        self.t_r3.setText(str(thresholds_r[3]))
        grid.addWidget(self.t_r0,5,3,1,1)
        grid.addWidget(self.t_r1,5,4,1,1)
        grid.addWidget(self.t_r2,5,5,1,1)
        grid.addWidget(self.t_r3,5,6,1,1)
        
        self.t_l0 = QtGui.QLabel()
        self.t_l1 = QtGui.QLabel()
        self.t_l2 = QtGui.QLabel()
        self.t_l3 = QtGui.QLabel()
        self.t_l0.setText(str(thresholds_l[0]))
        self.t_l1.setText(str(thresholds_l[1]))
        self.t_l2.setText(str(thresholds_l[2]))
        self.t_l3.setText(str(thresholds_l[3]))
        grid.addWidget(self.t_l0,6,3,1,1)
        grid.addWidget(self.t_l1,6,4,1,1)
        grid.addWidget(self.t_l2,6,5,1,1)
        grid.addWidget(self.t_l3,6,6,1,1)

        #plots
        self.plot0 = pg.PlotWidget()
        self.plot0.setLabel('left','Heel')
        self.plot0.setBackground('w')
        self.plot0.setYRange(0,3000)
        self.plot0.hideAxis('bottom')
        self.plot0.setMinimumWidth(600)
        grid.addWidget(self.plot0,0,0,1,10)  #row, col, rowspan, colspan (extend over 5 columns)
        self.plotcurve0 = pg.PlotCurveItem()
        self.plotcurve0.setData(pen='k')
        self.plot0.addItem(self.plotcurve0)
        
        self.plot1 = pg.PlotWidget()
        self.plot1.setLabel('left','Outside')
        self.plot1.setBackground('w')
        self.plot1.setYRange(0,3000)
        self.plot1.hideAxis('bottom')
        self.plot1.setMinimumWidth(600)
        grid.addWidget(self.plot1,1,0,1,10)
        self.plotcurve1 = pg.PlotCurveItem()
        self.plotcurve1.setData(pen='k')
        self.plot1.addItem(self.plotcurve1)
        
        self.plot2 = pg.PlotWidget()
        self.plot2.setLabel('left','Inside')
        self.plot2.setBackground('w')
        self.plot2.setYRange(0,3000)
        self.plot2.hideAxis('bottom')
        self.plot2.setMinimumWidth(600)
        grid.addWidget(self.plot2,2,0,1,10)
        self.plotcurve2 = pg.PlotCurveItem()
        self.plotcurve2.setData(pen='k')
        self.plot2.addItem(self.plotcurve2)
        
        self.plot3 = pg.PlotWidget()
        self.plot3.setLabel('left','Toe')
        self.plot3.setBackground('w')
        self.plot3.setYRange(0,3000)
        self.plot3.hideAxis('bottom')
        self.plot3.setMinimumWidth(600)
        grid.addWidget(self.plot3,3,0,1,10)
        self.plotcurve3 = pg.PlotCurveItem()
        self.plotcurve3.setData(pen='k')
        self.plot3.addItem(self.plotcurve3)
        
        #lines for thresholding
        self.t0 = pg.InfiniteLine(pos=500, pen={'width':2},movable=True, angle=0, bounds=[0,2500], label='x={value:1.0f}',labelOpts={'position':0.1, 'color': (200,200,100), 'movable': True})     
        self.t1 = pg.InfiniteLine(pos=500, pen={'width':2},movable=True, angle=0, bounds=[0,2500], label='x={value:1.0f}',labelOpts={'position':0.1, 'color': (200,200,100), 'movable': True})  
        self.t2 = pg.InfiniteLine(pos=500, pen={'width':2},movable=True, angle=0, bounds=[0,2500], label='x={value:1.0f}',labelOpts={'position':0.1, 'color': (200,200,100), 'movable': True})
        self.t3 = pg.InfiniteLine(pos=500, pen={'width':2},movable=True, angle=0, bounds=[0,2500], label='x={value:1.0f}',labelOpts={'position':0.1, 'color': (200,200,100), 'movable': True})
        self.plot0.addItem(self.t0)
        self.plot1.addItem(self.t1)
        self.plot2.addItem(self.t2)
        self.plot3.addItem(self.t3)
        
    def qt_connections(self):
        self.button.clicked.connect(self.on_button_clicked)
        self.resetbutton.clicked.connect(self.on_resetbutton_clicked)
        self.radiobutton_r.toggled.connect(self.on_radiobutton_toggled)
        
    def on_resetbutton_clicked(self):
        if self.radiobutton_r.isChecked():
            global r_s0
            global r_s1
            global r_s2
            global r_s3    
            r_s0 = np.empty([])
            r_s1 = np.empty([])
            r_s2 = np.empty([])
            r_s3 = np.empty([])
        elif self.radiobutton_l.isChecked():
            global l_s0
            global l_s1
            global l_s2
            global l_s3    
            l_s0 = np.empty([])
            l_s1 = np.empty([])
            l_s2 = np.empty([])
            l_s3 = np.empty([])
    
    def on_radiobutton_toggled(self):
        global thresholds_r
        global thresholds_l
        if self.radiobutton_r.isChecked():
            self.t0.setValue(thresholds_r[0])
            self.t1.setValue(thresholds_r[1])
            self.t2.setValue(thresholds_r[2])
            self.t3.setValue(thresholds_r[3])
        if self.radiobutton_l.isChecked():
            self.t0.setValue(thresholds_l[0])
            self.t1.setValue(thresholds_l[1])
            self.t2.setValue(thresholds_l[2])
            self.t3.setValue(thresholds_l[3])
        
    def on_button_clicked(self):      
        global calibrate_flag 
        calibrate_flag = True
        
    def update(self):
        if self.radiobutton_r.isChecked():
            global r_s0
            global r_s1
            global r_s2
            global r_s3
            global thresholds_r
            #plot the sensor values
            r_s0 = np.append(r_s0, np.array([sensors_R[0]]))
            r_s1 = np.append(r_s1, np.array([sensors_R[1]]))
            r_s2 = np.append(r_s2, np.array([sensors_R[2]]))
            r_s3 = np.append(r_s3, np.array([sensors_R[3]]))
            self.plotcurve0.setData(r_s0)       
            self.plotcurve1.setData(r_s1)
            self.plotcurve2.setData(r_s2)
            self.plotcurve3.setData(r_s3)
            thresholds_r[0] = int(self.t0.value())
            thresholds_r[1] = int(self.t1.value())
            thresholds_r[2] = int(self.t2.value())
            thresholds_r[3] = int(self.t3.value())
            self.t_r0.setText(str(int(self.t0.value())))
            self.t_r1.setText(str(int(self.t1.value())))
            self.t_r2.setText(str(int(self.t2.value())))
            self.t_r3.setText(str(int(self.t3.value())))
            
        elif self.radiobutton_l.isChecked():
            global l_s0
            global l_s1
            global l_s2
            global l_s3
            global thresholds_l
            #plot the sensor values
            l_s0 = np.append(l_s0, np.array([sensors_L[0]]))            
            l_s1 = np.append(l_s1, np.array([sensors_L[1]]))            
            l_s2 = np.append(l_s2, np.array([sensors_L[2]]))            
            l_s3 = np.append(l_s3, np.array([sensors_L[3]]))
            self.plotcurve0.setData(l_s0)
            self.plotcurve1.setData(l_s1)
            self.plotcurve2.setData(l_s2)
            self.plotcurve3.setData(l_s3)
            thresholds_l[0] = int(self.t0.value())
            thresholds_l[1] = int(self.t1.value())
            thresholds_l[2] = int(self.t2.value())
            thresholds_l[3] = int(self.t3.value())
            self.t_l0.setText(str(int(self.t0.value())))
            self.t_l1.setText(str(int(self.t1.value())))
            self.t_l2.setText(str(int(self.t2.value())))
            self.t_l3.setText(str(int(self.t3.value())))
        
        if calibrate_flag == True:
            #clear calibrate status
            self.label7.clear()
        elif calibrate_flag == False and calibrate_success == True:
            #show calibrate success message
            self.label7.setText('Calibration successful')
            
    def closeEvent(self, event):
        global r_s0
        global r_s1
        global r_s2
        global r_s3
        calibrate_flag == False
        self.timer.stop()
        r_s0 = np.empty([])
        r_s1 = np.empty([])
        r_s2 = np.empty([])
        r_s3 = np.empty([])
        event.accept()

            
#main window for the Xosoft logger    
class xosoft(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(xosoft, self).__init__(parent)        
        self.init_ui()
        self.qt_connections()
        self.connect_sockets()
        self.logstate = False
        self.msgid_list = []
        self.listresetCnt = 0
        self.wait_cnt = 0
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0.1)
        
    def init_ui(self):
        #set main window properties
        self.setWindowTitle('Xosoft raw data logger')
        self.setGeometry(100, 100, 200, 200)
        
        #mainwindow needs a widget to hold contents
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        
        #add a grid to the main window widget
        grid = QtGui.QGridLayout()
        grid.setColumnMinimumWidth(5,100)
        self.widget.setLayout(grid)
        
        pg.setConfigOptions(antialias=True)
        
        # buttons
        
        #calibrate shoe sensor button
        self.calibratebutton = QtGui.QPushButton("Calibrate shoe sensors")
        grid.addWidget(self.calibratebutton,1,1,1,2)
        
        #start and stop logging buttons
        self.logbutton = QtGui.QPushButton("Start logging")
        grid.addWidget(self.logbutton,2,1,1,2)
        
        #send command to nucleo to start sending data
        self.imubutton = QtGui.QPushButton("Start sending sensor data")
        grid.addWidget(self.imubutton,3,1,1,2)
        
        #send command to engage
        self.engupclubutton = QtGui.QPushButton("Engage upper clutch")
        grid.addWidget(self.engupclubutton,6,1,1,2)
        #send command to engage
        self.englowclubutton = QtGui.QPushButton("Engage lower clutch")
        grid.addWidget(self.englowclubutton,7,1,1,2)
        #send command to engage
        self.disengupclubutton = QtGui.QPushButton("Disengage upper clutch")
        grid.addWidget(self.disengupclubutton,8,1,1,2)
        #send command to engage
        self.disenglowclubutton = QtGui.QPushButton("Disengage lower clutch")
        grid.addWidget(self.disenglowclubutton,9,1,1,2)

        #send command to engage
        self.sendtimebutton = QtGui.QPushButton("Disengage delay 250ms")
        grid.addWidget(self.sendtimebutton,10,1,1,2)

        self.e0 = QtGui.QLineEdit()
        self.e0.setText("250")
        grid.addWidget(self.e0,10,3)
        
        self.e1 = QtGui.QLineEdit()
        self.e1.setText("sub07_b1a_nw")
        grid.addWidget(self.e1,15,1)
        
        self.e2 = QtGui.QLineEdit()
        self.e2.setText("01")
        grid.addWidget(self.e2,16,1)
                        
    def qt_connections(self):
        self.calibratebutton.clicked.connect(self.on_calibratebutton_clicked)

        self.logbutton.clicked.connect(self.on_logbutton_clicked)
        self.imubutton.clicked.connect(self.on_imubutton_clicked)
        
        self.engupclubutton.clicked.connect(self.on_engupclubutton_clicked)
        self.englowclubutton.clicked.connect(self.on_englowclubutton_clicked)
        
        self.disengupclubutton.clicked.connect(self.on_disengupclubutton_clicked)
        self.disenglowclubutton.clicked.connect(self.on_disenglowclubutton_clicked)
        
        self.sendtimebutton.clicked.connect(self.on_sendtimebutton_clicked)

    def connect_sockets(self):
        self.sensor0 = sensorClass.Sensor()
        self.sensor1 = sensorClass.Sensor()
        self.heneboard = heneClass2.Heneboard()
            
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
        self.socketlist = [self.sock2]
        
    def update(self):
        global calibrate_flag
        #try to read from each socket
        buf = bytearray(1024)        
        for idx, sock in enumerate(self.socketlist):
            try:
                inBytes = sock.recv_into(buf)
                if inBytes > 0:
                    self.parseData(buf, inBytes)
                    if self.logstate == False:
                        if not(buf[2] in self.msgid_list):
                            self.msgid_list.append(buf[2])
                        self.msgid_list.sort()
#                        print(self.msgid_list)                            
                        self.listresetCnt += 1
                        if self.listresetCnt > 1000:
                            self.listresetCnt = 0
                            #print("LIST RESET")
                            for i in range(len(self.msgid_list)):
                                del self.msgid_list[0]
                    else:
                        self.f.write( buf[:inBytes] )#self.print_data_to_file(buf)                          
            except socket.error:
                pass
        if calibrate_flag:
            #TODO: send threshold values to the heneboard, wait half a second for the reply
            self.wait_cnt = self.wait_cnt+1            
            if self.wait_cnt >= 500:
                self.wait_cnt = 0
                self.send_calibrate()
            
    
    def on_calibratebutton_clicked(self):    
        self.caldialog = Calibrate_dialog(self)
        self.caldialog.show()
    
    def on_logbutton_clicked(self):
        if self.logstate == False:
            self.logbutton.setText("Stop logging")
            self.heneboard.clear()
            
            print ("Logging started")
            self.logstate = True

            filename = "logs_werner/" + self.e1.text() + self.e2.text() + ".bin"
            #☺date = datetime.datetime.today()
            #filename = "log/log_%d%02d%02d_%02d%02d%02d.bin" % (date.year, date.month, date.day, date.hour, date.minute, date.second)
            self.f = open(filename,'wb+')

        else:
            print ("Logging stopped")
            self.f.close()
            
            self.heneboard.max_array_length = heneClass2.MAX_ARRAY_LEN
            self.logbutton.setText("Start logging")
            self.logstate = False
            self.showHene = True
            self.e2.setText(str(int(self.e2.text()) + 1).zfill(2))
    
    def on_imubutton_clicked(self):
        com = bytearray.fromhex("a5 01 ff 00 00")
        com[4] = (com[1]^com[2])^com[3]
        print("sending start command:",com[0],com[1],com[2],com[3],com[4])
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send start udp command")

    def on_engupclubutton_clicked(self):
        com = bytearray.fromhex("a5 01 C8 fe 00")
        com[4] = (com[1]^com[2])^com[3]
        print("sending start command:",com[0],com[1],com[2],com[3],com[4])
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send start udp command")

    def on_englowclubutton_clicked(self):
        com = bytearray.fromhex("a5 01 C8 ff 00")
        com[4] = (com[1]^com[2])^com[3]
        print("sending start command:",com[0],com[1],com[2],com[3],com[4])
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send start udp command")

    def on_disengupclubutton_clicked(self):
        com = bytearray.fromhex("a5 01 C8 fc 00")
        com[4] = (com[1]^com[2])^com[3]
        print("sending start command:",com[0],com[1],com[2],com[3],com[4])
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send start udp command")
            
    def on_disenglowclubutton_clicked(self):
        com = bytearray.fromhex("a5 01 C8 fd 00")
        com[4] = (com[1]^com[2])^com[3]
        print("sending start command:",com[0],com[1],com[2],com[3],com[4])
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send start udp command")

    def on_sendtimebutton_clicked(self):
        delay = int(self.e0.text())
        com = bytearray.fromhex("a5 01 C8 19 00")
        com[3] = int(delay/10)
        com[4] = (com[1]^com[2])^com[3]
        print("sending start command:",com[0],com[1],com[2],com[3],com[4])
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send start udp command")
    
    def send_calibrate(self):
        com = bytearray.fromhex("a5 08 05 00 00 00 00 00 00 00 00 00")
        com[3] = thresholds_r[0] & 255
        com[4] = thresholds_r[0] >> 8
        com[5] = thresholds_r[1] & 255
        com[6] = thresholds_r[1] >> 8
        com[7] = thresholds_r[2] & 255
        com[8] = thresholds_r[2] >> 8
        com[9] = thresholds_r[3] & 255
        com[10] = thresholds_r[3] >> 8
        com[11] = ((((((((com[1]^com[2])^com[3])^com[4])^com[5])^com[6])^com[7])^com[8])^com[9])^com[10]
        print("com:",com[3],com[4],com[5],com[6],com[7],com[8],com[9],com[10])
        print("sending calibrate command right:",thresholds_r)
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send calibrate command right")
        com = bytearray.fromhex("a5 08 06 00 00 00 00 00 00 00 00 00")
        com[3] = thresholds_l[0] & 255
        com[4] = thresholds_l[0] >> 8
        com[5] = thresholds_l[1] & 255
        com[6] = thresholds_l[1] >> 8
        com[7] = thresholds_l[2] & 255
        com[8] = thresholds_l[2] >> 8
        com[9] = thresholds_l[3] & 255
        com[10] = thresholds_l[3] >> 8
        com[11] = ((((((((com[1]^com[2])^com[3])^com[4])^com[5])^com[6])^com[7])^com[8])^com[9])^com[10]
        print("com:",com[3],com[4],com[5],com[6],com[7],com[8],com[9],com[10])
        print("sending calibrate command left:",thresholds_l)
        try:
            self.sock2.sendto(com, ("192.168.0.100", 14551))
        except socket.error:
            print("socket",self.sock2,"could not send calibrate command left")
            
    #parse received data and check if multiple packets were received at once
    def parseData(self, buf, inBytes):
        global calibrate_flag
        global calibrate_success
        
        buf = buf[:inBytes]
        while len(buf) > 0:
            if buf[0] == START_BYTE:
                pktsize = buf[1]+4
                if len(buf) < pktsize: break
                if buf[2] == FOOT_R: 
                    if buf[1] == 10:    #raw data
                        sensors_R[0] = buf[5] + (buf[6]<<8)
                        sensors_R[1] = buf[7] + (buf[8]<<8)
                        sensors_R[2] = buf[9] + (buf[10]<<8)
                        sensors_R[3] = buf[11] + (buf[12]<<8)
                    elif buf[1] == 8:   #threshold data
                        print('right foot packet:',end='')    
                        for i in range(0,pktsize):                    
                            print(buf[i], end=' ')
                        print(' ')
                        tmp = [0,0,0,0]
                        tmp[0] = buf[3] + (buf[4] << 8)
                        tmp[1] = buf[5] + (buf[6] << 8)
                        tmp[2] = buf[7] + (buf[8] << 8)
                        tmp[3] = buf[9] + (buf[10] << 8)
                        for i in range(0,4):
                            if tmp[i] != thresholds_r[i]:
                                calibrate_success = False
                                break
                            else: 
                                calibrate_success = True
                        calibrate_flag = False
                            
                elif buf[2] == FOOT_L:
                    if buf[1] == 10: #raw data
                       sensors_L[0] = buf[5] + (buf[6]<<8)
                       sensors_L[1] = buf[7] + (buf[8]<<8)
                       sensors_L[2] = buf[9] + (buf[10]<<8)
                       sensors_L[3] = buf[11] + (buf[12]<<8)     
                    elif buf[1] == 8:   #threshold data
                        print('left foot packet:',end='')
                        for i in range(0,pktsize):                    
                            print(buf[i], end=' ')
                        print(' ')
                buf = buf[pktsize:]
            else:
                buf = buf[1:]
            
    def print_data_to_file(self,data):        
        for i in range(0,(len(data)-1)):
            self.f.write( data[i] )
          #  print(data[i], file=self.f)
            
    def closeEvent(self, event):
        try:
            self.sock2.shutdown(socket.SHUT_RDWR)
            self.sock2.close()
        except:
            pass
        if self.logstate:   #stop logging when closed
            self.on_logbutton_clicked()
        print("Window closed -> Sockets disconnected")
        event.accept()

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('xosoft')
    main = xosoft()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


#sample code to send http request direct to the wifi module
#            self.sock2.bind((UDP_IP2, UDP_PORT2))
#        try:
#            f=requests.get('http://192.168.0.11:80', timeout=3)
#            print(f.status_code)
#            if f.status_code == 200:
#                print("status ok, sending new calibration data")
#                #TODO: send data here
#
#        except requests.Timeout:            
#            self.messageLabel.setText("Timeout")
#            print("timeout connecting to module")

                #get max and min values for the sensors
#                for ii in range(0,4):
#                    if sensors_R[ii] > max_R[ii]:
#                        max_R[ii] = sensors_R[ii]                        
#                for ii in range(0,4):
#                    if sensors_R[ii] < min_R[ii]:
#                        min_R[ii] = sensors_R[ii]
