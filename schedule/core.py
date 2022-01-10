# -*- coding: utf-8 -*-
import threading
import schedule
import time

global one, two

def job_1():
    print("---job_1 start ... " + one)
    time.sleep(10)
    print("---job_1 end ...")

def job_2():
    print("---job_2 start ... ")
    time.sleep(10)
    print("---job_2 end ...")

def job_3():
    print("---job_3 start ... " + two)
    time.sleep(10)
    print("---job_3 end ..." + two)

def show_all_jobs():
    all_jobs = schedule.get_jobs()
    for job in all_jobs:
        print(job)

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

# 多任务默认为串型执行, 使用threading开启多线程
# 按时间发起任务, 不等待任务执行结果
if __name__ == "__main__":
    # schedule.every().thursday.at('21:05').do(job_2)
    # schedule.every().minute.at(":05").do(job_1)
    one, two = "one_test", "two_test"
    schedule.every(4).seconds.do(run_threaded, job_1)
    schedule.every(4).seconds.do(run_threaded, job_2)
    schedule.every(4).seconds.do(run_threaded, job_3)
    schedule.every(9).seconds.do(run_threaded, show_all_jobs)
    while True:
        schedule.run_pending()
        time.sleep(1)
