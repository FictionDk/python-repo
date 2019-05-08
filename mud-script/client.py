import websocket
try:
	import thread
except ImportError:
	import _thread as thread
import time

def on_message(ws,message):
	print(message)

def on_error(ws,error):
	print(error)

def on_close(ws):
	print("### closed ###")

def on_open(ws):
	

if __name__ = "__main__":
	websocket.enableTrace(True)
	ws = websocket.WebsocketApp("ws://120.78.75.229:25631/")