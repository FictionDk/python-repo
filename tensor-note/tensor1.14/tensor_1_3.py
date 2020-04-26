# -*- coding: utf-8 -*-
import pickle
import os

def file_dump_test():
    game_data = {
        "position":"N2 E3",
        "pocket":["keys","knife"],
        "mondy": 160
    }
    save_file = open("save.dat","wb")
    pickle.dump(game_data,save_file)
    save_file.close()

def file_load_test():
    load_file = open(os.getcwd() + os.sep + "save.dat",'rb')
    load_game_data = pickle.load(load_file)
    load_file.close()
    print(load_game_data)
    pass

def main():
    file_dump_test()
    file_load_test()

if __name__ == "__main__":
    main()
