from pyModbusTCP.client import ModbusClient

c = ModbusClient(host='127.0.0.1',port=502)
print(c)
if c.open():
    reg_list_1 = c.read_holding_registers(0,10)
    reg_list_2 = c.read_holding_registers(55,10)
    print(reg_list_1)
    print(reg_list_2)
    c.close()
