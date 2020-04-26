# -*- coding: utf-8 -*-
class Animals(object):
    def __init__(self, arg):
        super(Animals, self).__init__()
        self.arg = arg

    def breath(self):
        print("breathing")

    def move(self):
        print("moving")

    def eat(self):
        print("eating")

class Mammals(Animals):
    def breastfeed(self):
        print("feeding young")

class Cats(Mammals):
    def __init__(self,spots):
        self.spots = spots

    def catch_mouse(self):
        print("catch mouse")

    def __left_foot_forward(self):
        print("left foot forward")

    def __left_foot_backword(self):
        print("left foot backword")

    def dance(self):
        for i in range(0,4):
            self.__left_foot_forward()
            self.__left_foot_backword()

def main():
    kitty = Cats(10)
    print(kitty.spots)
    kitty.dance()
    kitty.breastfeed()
    kitty.move()
    # 私有方法
    # kitty.__left_foot_backword()

if __name__ == "__main__":
    main()
