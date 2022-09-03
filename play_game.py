# from decode import connectSerial
import numpy as np
import matplotlib.pyplot as plt
import time
import argparse
import pyautogui

def play(t, pos_act):
    nowTime = millis()
    ptr = 0
    print("Start")
    while True:
        if ptr >= len(t):
            print("End of the song")
            break
        if abs(millis() - nowTime - t[ptr]) < 10:
            try:
                # k = int(len(pos_act[ptr]) /2)
                # for i in range(k):
                #     if pos_act[ptr][i*2] == "3":
                seri.write(pos_act[ptr])
                ptr += 1
            except:
                return 


# if __name__ == '__main__':
    # se = connectSerial()
    # if se == None:
    #     exit()

    # time.sleep(2)
    # input("Can start in anytime")
    # play(se, s_, q_)

