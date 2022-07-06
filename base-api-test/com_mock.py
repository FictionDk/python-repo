# -*- coding: utf-8 -*-

from socket import timeout
import serial
import time
from serial import SerialException

def set_com_value(comNumber, value):
    flag = True
    while flag:
        try:
            ser = serial.Serial(comNumber, baudrate=9600, parity=serial.PARITY_ODD, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, timeout=0.5)
            print(ser)
            r = ser.write((value).encode('utf-8'))
            print("打开串口{0},写入结果{1}".format(ser.name,r))
            flag = False
        except SerialException:
            print("打开串口{0},失败".format(comNumber))
            time.sleep(0.5)

def setPlateVal():
    set_com_value('COM8','2207041171\r\n')
    set_com_value('COM6','2207041172\r\n')

def set_plc_val():
    set_com_value('COM2','%01$RD010001000000000001000100000016\r\n')

def setLabelVal():
    pre_val = '220714B000'
    for i in range(3):
        set_com_value('COM10',pre_val+str(i)+"\r\n")
        # set_com_value('COM12',pre_val+str(i*2)+"\r\n")
        time.sleep(1)


if __name__ == "__main__":
    setPlateVal()
    time.sleep(3)
    setLabelVal()
    set_plc_val()
