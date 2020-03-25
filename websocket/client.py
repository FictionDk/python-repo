# -*- coding: utf-8 -*-
import websocket
try:
    import thread
except ImportError:
    import _thread as thread

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
    return "ws://127.0.0.1:10001/console/1001"
    # return "ws://127.0.0.1:8021/im/1001"

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(get_uri(), on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
