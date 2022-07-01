# -*- coding: utf-8 -*-

from socket import timeout
import serial
import time
from serial import SerialException

def set_com_value(comNumber, value):
    flag = True
    while flag:
        try:
            ser = serial.Serial(comNumber, baudrate=9600, parity=serial.PARITY_ODD, bytesize=serial.EIGHTBITS, timeout=0.5)
            print(ser)
            r = ser.write((value).encode('utf-8'))
            print("打开串口{0},写入结果{1}".format(ser.name,r))
            flag = False
        except SerialException:
            print("打开串口{0},失败".format(comNumber))
            time.sleep(0.5)

def set_1Com():
    set_com_value('COM6','B21C2A31')

if __name__ == "__main__":
    set_1Com()
    time.sleep(3)