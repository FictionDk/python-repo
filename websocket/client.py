# -*- coding: utf-8 -*-
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import os
import json
import sys

WORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
FILE_UTIL_DIR = os.path.join(WORK_DIR,"file-opt")
sys.path.append(FILE_UTIL_DIR)
import file_utils

class CannotReadFile(RuntimeError):
    pass

def _get_conf_from_file(filepath):
    '''读取指定路径的配置文件内容,返回table
    Args:
        filepath: 文件全路径字符串,如`/root/pwd/config.jl`
    Returns:
        返回文件的全路径
    Raises:
        ConfigIsNone: 无法从配置文件读取内容
    '''
    conf_str = None
    conf_json = {}
    with open(filepath,'r',encoding="utf-8") as f:
        conf_str = f.readline()
        if len(conf_str) > 0:
            conf_json = json.loads(conf_str)
    if(conf_json == {}):
        raise CannotReadFile('[%s] must fill with content like \
        {"username": "xx","userid": "xx", "ip":"192.168.3.1", "port": 22}' % filepath)
    return conf_json

def get_conf():
    '''读取源服务连接配置
    Returns: username, userid, ip, port
    '''
    conf_path = file_utils.get_full_filename('config','websocket_conf.jl')
    conf_json = _get_conf_from_file(conf_path)
    source_list = list(conf_json.values())
    return source_list[0], source_list[1], source_list[2], source_list[3]

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        flag = True
        while flag:
            line = input()
            if line == 'exit':
                flag = False
            else:
                ws.send(line)
            pass
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())

def get_uri():
    username, userid, ip, port = get_conf()
    conn = "ws://%s:%d/console/%s/%s" % (ip, port, userid, username)
    return conn

def main():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(get_uri(), on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

def test():
    username, userid, ip, port = get_conf()
    print(username, userid, ip, port)

if __name__ == "__main__":
    main()
