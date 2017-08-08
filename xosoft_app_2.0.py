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
import heneClass

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
        self.checkbox_hene.clicked.connect(self.on_checkbox_hene_clicked)
        self.checkbox_left.clicked.connect(self.on_checkbox_left_clicked)
        self.checkbox_right.clicked.connect(self.on_checkbox_right_clicked)

    def connect_sockets(self):
        self.sensor0 = sensorClass.Sensor()
        self.sensor1 = sensorClass.Sensor()
        self.heneboard = heneClass.Heneboard()
        
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
                data, addr = sock.recvfrom(64)
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
#                    print(ord(temp[0]),temp[1],ord(temp[2]),ord(temp[3]),ord(temp[4]),ord(temp[5]),ord(temp[6]),ord(temp[7]),ord(temp[8]))
                     heneClass.parseData(self.heneboard, data, idx, time.time())
 #                    self.heneboard.printData()
                     self.heneboard.addXY()
                     if len(self.heneboard.y_deltats) > 2:
                         if self.logstate:
                             print('heneboard',
                                   self.heneboard.counter,
                                   self.heneboard.ts,
#                                   self.heneboard.syncswitch,
#                                   self.heneboard.data0,
#                                   self.heneboard.data1,
#                                   self.heneboard.data2,
#                                   self.heneboard.data3,
#                                   self.heneboard.data4,
#                                   self.heneboard.data5,
#                                   self.heneboard.data6,
#                                   self.heneboard.data7,
#                                   self.heneboard.data8,
#                                   self.heneboard.data9,
#                                   self.heneboard.data10,
                                   file=self.f)

                         if self.showHene:
                             pass
 #                            self.plotcurve_hene0.setData(self.heneboard.x, self.heneboard.y_data0)
 #                            self.plotcurve_hene1.setData(self.heneboard.x, self.heneboard.y_data1)
 #                            self.plotcurve_hene2.setData(self.heneboard.x, self.heneboard.y_data2)
#                             self.plotcurve_hene3.setData(self.heneboard.x, self.heneboard.y_data3)
 #                            self.plotcurve_hene4.setData(self.heneboard.x, self.heneboard.y_data4)
 #                            self.plotcurve_hene5.setData(self.heneboard.x, self.heneboard.y_data5)
 #                            self.plotcurve_hene6.setData(self.heneboard.x, self.heneboard.y_data6)
 #                            self.plotcurve_hene7.setData(self.heneboard.x, self.heneboard.y_data7)
 #                            self.plotcurve_hene8.setData(self.heneboard.x, self.heneboard.y_data8)
 #                            self.plotcurve_hene9.setData(self.heneboard.x, self.heneboard.y_data9)
 #                            self.plotcurve_hene10.setData(self.heneboard.x, self.heneboard.y_data10)
                         self.heneMissedPackets.setText(str(self.heneboard.missedPackets))

            except socket.error:
                pass
    
        
    def on_logbutton_clicked(self):
        if self.logstate == False:
            self.logbutton.setText("Stop logging")
            
            print ("Logging started")
            self.checkbox_hene.setChecked(False)
            self.checkbox_left.setChecked(False)
            self.checkbox_right.setChecked(False)
            self.showHene = False
            self.showLeft = False
            self.showRight = False
            
            date = datetime.datetime.today()
            filename = "log_%d%02d%02d_%02d%02d%02d.csv" % (date.year, date.month, date.day, date.hour, date.minute, date.second)
            self.f = open(filename,'w')
            self.logstate = True
            print("Sensor Counter Timestamp ADC0 ADC1 ADC2 ADC3\n"
              "Heneboard Counter timestamp Syncswitch data0 data1 data2 data3 data4 data5 data6 data7 data8 data9 data10", file=self.f)
        else:
            print ("Logging stopped")
            self.logbutton.setText("Start logging")
            self.logstate = False
            self.f.close()
            self.checkbox_hene.setChecked(True)
            self.checkbox_left.setChecked(True)
            self.checkbox_right.setChecked(True)
            self.showHene = True
            self.showLeft = True
            self.showRight = True
        
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
        
def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('xosoft')
    ex = xosoft()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
