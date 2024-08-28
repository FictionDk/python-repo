import psutil # 5.9.0
import requests
import time

WARNING_THRESHOLD = 85  # 内存使用率的预警阈值
CHECK_INTERVAL = 30  # 检查间隔时间（秒）
DING_HOOK_TOKEN = "xxx"

class StateMachine:
    def __init__(self, threshold=90):
        self.threshold = threshold
        self.state = "normal"  # 初始状态为正常
        self.notified = {"normal": False, "abnormal": False}

    def update(self, value):
        if value > self.threshold:
            self.change_state("abnormal", value)
        else:
            self.change_state("normal", value)

    def change_state(self, new_state, val):
        if self.state != new_state:
            self.state = new_state
            self.notify(val)

    def notify(self, val):
        if self.state == "normal" and not self.notified["normal"]:
            self.notified["normal"] = True
            self.notified["abnormal"] = False
            send_ding_talk(f'系统内存恢复,10.20.28.99机器内存使用率:{str(val)}')
        elif self.state == "abnormal" and not self.notified["abnormal"]:
            self.notified["abnormal"] = True
            self.notified["normal"] = False
            send_ding_talk(f'系统内存预警,10.20.28.99机器内存使用率:{str(val)}')

def send_ding_talk(msg:str):
    hookUrl = f'https://oapi.dingtalk.com/robot/send?access_token={DING_HOOK_TOKEN}'
    content = {'msgtype': 'text', 'text': {'content': msg, 'at': {"atMobiles":["15155410918"],'isAtAll':False}}}
    requests.post(hookUrl, json=content)

def monitor_memory():
    """监控内存使用情况"""
    send_ding_talk(f"系统内存监控开启[10.20.28.99]")
    state_machine = StateMachine(threshold=WARNING_THRESHOLD)
    while True:
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        print(f"Current memory usage: {memory_usage}%")
        state_machine.update(memory_usage)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_memory()