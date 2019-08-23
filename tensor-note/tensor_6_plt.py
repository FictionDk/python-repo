# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

def test_1():
    fig = plt.figure("Test-01")
    ax = fig.add_subplot(3 4 9)
    ax.plot(x,y)
    plt.show()

def main():
    test_1()

if __name__ == '__main__':
    main()
