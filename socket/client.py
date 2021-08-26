# -*- coding: utf-8 -*-
import socket

def time_req():
    try:
        client = socket.socket()
        client.connect(('127.0.0.1',8089))
        client.send(bytes('QUERY TIME ORDER\n',encoding='utf-8'))
        print("Waiting...")
        data = client.recv(1024)
        print("Geting..." + str(data))
        if data:
            print(data.decode())
    except ConnectionResetError:
        print('连接中断！')
    except ConnectionRefusedError:
        print('连接被拒绝')
    else:
        client.close()

req_bytes = [-120, 0, 0, 0, 50, 49, 48, 48, 48, 56, 48, 56, 54, 55, 52, 51, 53, 48, 53, 50, 50, 52, 
48, 57, 52, 50, 65, 57, 48, 48, 48, 48, 49, 54, 50, 57, 52, 54, 48, 49, 57, 55, 43, 76, 77, 83, 89, 83, 
61, 82, 70, 58, 49, 48, 48, 44, 66, 65, 84, 58, 57, 57, 44, 80, 82, 79, 58, 48, 44, 71, 80, 82, 83, 58, 
48, 48, 49, 50, 48, 44, 71, 80, 83, 58, 48, 48, 48, 51, 48, 44, 68, 84, 58, 49, 54, 50, 57, 52, 54, 48, 
49, 57, 55, 44, 68, 73, 70, 70, 58, 50, 56, 56, 48, 48, 44, 87, 69, 65, 82, 58, 49, 13, 10, 43, 76, 77, 
70, 87, 61, 71, 69, 84, 13, 10, -90, 29]

cmd_sys = '+LMSYS=RF:100,BAT:99,PRO:0,GPRS:00120,GPS:00030,DT:1629460197,DIFF:28800,WEAR:1\r\n'
cmd_fw = '+LMFW=GET\r\n'
cmd_fota = '+LMFOTA=GET,V:V006,PN:0\r\n'

# 基础转换
def base_trans():
    b = b'\x88\x00\x00\x00'
    print(b)
    # 把bytes类型的变量x，转化为十进制整数
    # byteorder=little/big
    # 输出: 136 类型: int
    print(int.from_bytes(b, byteorder="little"))
    # 输出 b'\x88\x00\x00\x00' 类型: bytes
    print((136).to_bytes(4, byteorder="little"))
    # 16进制转10进制
    # 输出 136 类型: int
    print(int('0x88',16))
    # 10进制转16进制
    # 输出 0x32 类型: str
    print(hex(50))
    # 输出字节码,十进制
    for i in b:
        print(i)
    print("-----------------")
    b = b'\xa6\x1d'
    print(int.from_bytes(b, byteorder="little"))
    print((7590).to_bytes(2, byteorder="little"))
    print("-----------------")

def build_bytes():
    b_version = '2'
    b_type = '1'
    b_cid = '00080'
    b_imei = '867435052240942'
    b_uuid = 'A900001629460197'
    # content = [cmd_sys,cmd_fw,cmd_fota]
    content = [cmd_fota]
    b_len = 44
    for c in content:
        b_len += len(c)
    bs = (b_len).to_bytes(4, byteorder="little")
    bs += (b_version+ b_type + b_cid + b_imei + b_uuid).encode()
    for c in content:
        bs += c.encode()
    print(bs)
    for i in bs:
        print(hex(i).replace('0x',''), end=" ")
    print("\n-----------------")
    crc = build_crc(bs)
    print("check crc = ",crc)
    bs += (crc).to_bytes(2, byteorder="little")
    print("-----------------")
    return bs

def build_crc(data, byteorder='little'):
    length = len(data)
    checksum = 0
    for i in range(0, length):
        checksum += (0xff & data[i])
        # print(data[i],"+=",(0xff & data[i]),"=",checksum,end=",")
    return checksum

def asc2byte():
    base_trans()
    build_bytes()

def write_bytes(index, bs):
    with open(index+".log", 'wb') as f:
        f.write(bs)

def ota_req():
    client = socket.socket()
    client.connect(('127.0.0.1',8023))
    client.send(build_bytes())
    data = client.recv(1024)
    print("Geting..." + str(data))
    if data:
        print(data.decode())

ota_req()