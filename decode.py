import cv2
import re
import math
import numpy as np
import os
import argparse
from play_game import play
import serial

script_name = '10Pool_Master_75'

def checkAvailableSerial():
    ports = ['COM%s' % (i + 1) for i in range(256)] 
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def connectSerial():
    try:
        ports = checkAvailableSerial()
        if len(ports) == 0:
            print("Cannot find any ports")
            return None
        s = serial.Serial(port=str(ports[-1]), baudrate=115200, timeout=.1)
        print("Opened " + ports[-1])
    except:
        print("Cannot open port COM")
        s= None
    return s

def checkTurn(a, s):
    for i in range(5):
        if len(a[i]) >= 2 and ((a[i][-1][0]%10 == 3 and a[i][-2][0]%10 == 2) or (a[i][-1][0]%10 == 3 and a[i][-2][0]%10 == 7)\
                           or (a[i][-1][0]%10 == 2 and a[i][-2][0]%10 == 3) or (a[i][-1][0]%10 == 2 and a[i][-2][0]%10 == 8))\
                         and a[i][-1][1] - a[i][-2][1] <= 400:
            if len(s) == 0 or a[i][-1][1] != s[-1][2]:
                l = 0
                if (a[i][-1][0]%10 == 3 and a[i][-2][0]%10 == 2) or (a[i][-1][0]%10 == 3 and a[i][-2][0]%10 == 7):
                    l = len(a[i-1]) - 1 
                elif (a[i][-1][0]%10 == 2 and a[i][-2][0]%10 == 3) or (a[i][-1][0]%10 == 2 and a[i][-2][0]%10 == 8):
                    l = len(a[i+1]) - 1 
                s.append([l, a[i][-1][0], a[i][-1][1]])

def getDataFromFile(f):
    text = f.readlines()
    length_o = float(text[-2])
    duration = float(text[-1])
    text = text[:-2]
    first_frame = text[0].split(" ")[-1]
    storage = [[],[],[],[],[]]
    turn = []
    for cmd in text:
        [val, frame] = cmd[:-1].split(' ')
        pos = math.floor(int(val)/10)
        if frame != "F":
            t = ((float(frame)-float(first_frame)) / length_o  * duration)

            # 2nd position need to press slower
            if int(int(val)/10) == 2:
                t += 0.025
            # Release is deteced after the notes are ended. So time should be shifted forward
            if int(val)%10 > 5:
                t -= 0.125 # 0.075
                # To prevent overwrite the previous note if they are too close
                if len(storage[pos-1]) > 0 and (t * 1000) < storage[pos-1][-1][1]:
                    t = storage[pos-1][-1][1] / 1000 + 0.005
            # Left & Right & Forward is only detected when you sweep. The down action should be done before the note arrives
            if int(val)%10 != 1 and int(val)%10 != 5 and int(val)%10 != 6:
                if int(val)%10 > 5:
                    t -= 0.025
                else: 
                    t -= 0.05  # 0.04
                if int(int(val)/10) == 2:
                    t += 0.025
                # To prevent overwrite the previous note if they are too close
                if len(storage[pos-1]) > 0 and (t * 1000) < storage[pos-1][-1][1]:
                    t = storage[pos-1][-1][1] / 1000 + 0.005
            storage[pos-1].append([int(val), int(t*1000)])       
            checkTurn(storage, turn)
        else:
            storage[pos-1].pop()

    # Process turn
    true_turn = []
    for l, v, t in turn:
        if v%10 == 3:
            true_turn.append(storage[int(v/10)-2][l])
        elif v%10 == 2:
            true_turn.append(storage[int(v/10)][l])
    # Flatten the array 
    storage = [posnact for line in storage for posnact in line]
    # Change Turn
    for i in range(len(storage)):
        if storage[i] in true_turn:
            if storage[i][0]%10 == 2:
                storage[i] = [str(int(storage[i][0]/10)) + ";", storage[i][1]]
            elif storage[i][0]%10 == 3:
                storage[i] = [str(int(storage[i][0]/10)) + ":", storage[i][1]]
    # Mirror the array
    storage = [s[::-1] for s in storage]
    # Sort with the time
    storage.sort()

    # # Merge action if share the same time
    for i in range(len(storage)):
        if storage[i][0] == storage[i-1][0]:
            storage[i-1].append(storage[i][1])
            storage[i][0] = -1
    storage = [i for i in storage if i[0] != -1]
    return storage

def startDecoding(script_name):
    file_path = os.path.dirname(os.path.realpath(__file__))
    try:  
        f = open(file_path+'/File/'+script_name+'.txt', "r")
    except:
        print("Unable to open " + file_path+'/File/'+script_name+'.txt')
        return 
    storage = getDataFromFile(f)
    pos_act, t = [], []
    for i in range(len(storage)):
        t.append(storage[i].pop(0))
    for i in storage:
        if len(i)==1:
            pos_act.append((str(i[0])+'\n').encode())
        else:
            pos_act.append(("".join([str(j) for j in i])+'\n').encode())

    f.close()
    print("Done Decoding")   
    return pos_act, t


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image Stitching')
    parser.add_argument('--script', type=str, default=script_name,
                        help='name of the script, cannot include japanese')
    args = parser.parse_args()

    se = connectSerial()
    if se == None:
        exit()
    pos_act, t = startDecoding(args.script)
    input("Can start in anytime")
    play(se, t, pos_act)
