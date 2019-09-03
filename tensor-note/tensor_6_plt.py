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

def plt_figs_show():
    plt.figure("fig_1")  # 编号fig_1的figure
    plt.subplot(211)   # fig_1中的第一个子图
    plt.plot([1,3,4],'r')
    plt.subplot(212)  # fig_1中的第二个子图
    plt.plot([4,5,6])

    plt.figure("fig_2")  # 编号fig_2的figure
    # 默认使用subplot(111),此时fig_2为当前figure
    plt.plot([7,8,9],'g^',[7,8,9],'b')

    plt.figure("fig_1")  # 切换当前figure
    plt.subplot(212)  # 切换fig_1的子图
    plt.title('Easy fig_1 4,5,6')  # 为选取子图添加标题

    plt.show()

def plt_grid_show():
    mu,sigma = 100,15
    x = mu + sigma * np.random.randn(10000)

    # 绘制直方图
    n,bins,patches = plt.hist(x,50,density=10,color='g')
    plt.hist
    print(n)
    print(bins)
    print(patches)

    plt.xlabel('Smarts')
    plt.ylabel('Probality')
    plt.title('Histogram of IQ')
    # 位置(60,0.025) r表示后面的字符串是纯粹字符串
    plt.text(60,0.025,r'$\mu=100,sigma=15$')
    plt.axis([40,160,0,0.03])
    plt.grid(True)
    plt.show()

def main():
    # plt_show1()
    # plt_show2()
    # plt_fig_show0()
    # plt_figs_show()
    plt_grid_show()

if __name__ == "__main__":
    main()
