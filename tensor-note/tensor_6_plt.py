# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

def plt_show0():
    plt.plot([1,2,3,4])
    plt.ylabel('Numbers')
    plt.show()

def plt_show1():
    # 设置点(1,1) (2,4) (3,9) ...
    plt.plot([1,2,3,4],[1,4,9,16],'ro')
    # 设置x轴范围0~6 y轴0~20
    plt.axis([0,6,0,20])
    plt.show()

def plt_show2():
    t = np.arange(0.,5.,0.2)
    print(t.shape)
    print(t)
    # 红色 -- 蓝色 s(方块) 绿色^(三角)
    plt.plot(t,t,'r--',t,t**2,'bs',t**3,'g^')
    plt.show()

def dat_f0(t):
    return np.exp(-t) * np.cos(2 * np.pi * t)
def plt_fig_show0():
    t1 = np.arange(0.0,5.0,0.1)
    t2 = np.arange(0.0,5.0,0.2)

    plt.figure("Title")
    plt.subplot(211)
    plt.plot(t1,dat_f0(t1),'bo',t2,dat_f0(t2),'k')

    plt.subplot(212)
    plt.plot(t2,np.cos(2 * np.pi * t2),'r--')

    plt.show()

def main():
    # plt_show1()
    # plt_show2()
    plt_fig_show0()

if __name__ == "__main__":
    main()
