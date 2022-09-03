import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import argparse
from multiprocessing import Process, Manager
import os
from decode import startDecoding, connectSerial
from play_game import play

name_of_song = "10Pool_Master_75"
speed_of_song = 78

def getPos(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        print('({}, {})'.format(x, y))

def getScreenPos(cap):
    screen_pos = [[0,0],[0,0],[0,0],[0,0]]   
    while True:
        _, frame = cap.read()
        if frame is None:
            return
        arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        arucoParams = cv2.aruco.DetectorParameters_create()
        (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams) 
        # verify FOUR ArUco markers were detected
        if len(corners) == 4:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            # loop over the detected ArUCo corners
            for (markerCorner, markerID) in zip(corners, ids):
                # extract the marker corners (which are always returned in
                # top-left, top-right, bottom-right, and bottom-left order)
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
                # convert each of the (x, y)-coordinate pairs to integers
                topRight = [int(topRight[0]), int(topRight[1])]
                bottomRight = [int(bottomRight[0]), int(bottomRight[1])]
                bottomLeft = [int(bottomLeft[0]), int(bottomLeft[1])]
                topLeft = [int(topLeft[0]), int(topLeft[1])]
                diff = [abs(bottomLeft[0] - topRight[0])/2,abs(bottomLeft[1] - topRight[1])/2]
                # print(markerID,topLeft, topRight, bottomLeft, bottomRight)
                # # draw the bounding box of the ArUCo detection
                cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                # compute and draw the center (x, y)-coordinates of the ArUco
                # marker
                # cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                # cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                # cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
                # draw the ArUco marker ID on the image
                # cv2.putText(frame, str(markerID),
                #     (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                #     0.5, (0, 255, 0), 2)
                # print("[INFO] ArUco marker ID: {}".format(markerID))
                screen_pos[markerID-1] = [[topLeft[0]-diff[0],topLeft[1]+diff[1]], 
                                            [topRight[0]-diff[0],topRight[1]-diff[1]],
                                            [bottomLeft[0]+diff[0],bottomLeft[1]+diff[1]],
                                            [bottomRight[0]+diff[0],bottomRight[1]-diff[1]]]
            return screen_pos
            break
        cv2.imshow("Calibrating Screen", frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            # return screen_pos
            break

def decreaseLightIntensity(frame, val):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h,s, v = cv2.split(hsv)
    v[v<val] = val
    v -= val
    final_hsv = cv2.merge((h, s, v))
    return final_hsv

def increaseLightIntensity(frame, val):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h,s, v = cv2.split(hsv)
    v[v>(255-val)] = 255-val
    v += val
    final_hsv = cv2.merge((h, s, v))
    return final_hsv

def songReadyToBegin(frame, d):
    # hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # mask = cv2.inRange(hsv_frame,(0,0,186), (179, 255, 255))
    # mask = mask[308:387,118:616]
    # mask = cv2.dilate(mask, np.ones((10,10), np.uint8), iterations=1)
    # contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # i=0
    # for cnt in contours:
    #     if cnt.size > 90:
    #         i += 1
    #         x,y,w,h = cv2.cv2.boundingRect(cnt)
    #         cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 3)
    # if i>=5:
    #     return True

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame,(85,50,255), (90, 120, 255))
    mask = mask[100:107, 495:595]
    if np.count_nonzero(mask) / (len(mask) * len(mask[0])) > 0.2:
        if d['Test']:
            print("Can detect START !!!")
        return True
        
    return False

def firstNoteDown(initCap, frame, d):
    hsv_frame = increaseLightIntensity(frame, 0)
    mask = cv2.inRange(hsv_frame,(0,0,186), (179, 255, 255))
    mask = mask[140:194,118:619] - initCap
    if np.count_nonzero(mask) / (len(mask) * len(mask[0])) > 0.04:
        if d['Test']:
            print("Can detect FIRST NOTE !!!")
        # else:
        return True
    return False

    # initCap, frame = initCap[140:194,118:619], frame[140:194,118:619]


def checkSongEnd(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame,(0,0,186), (179, 255, 255))
    mask = mask[308:387,118:616]
    mask = cv2.dilate(mask, np.ones((10,10), np.uint8), iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    i=0
    for cnt in contours:
        if cnt.size > 90:
            i += 1
            # x,y,w,h = cv2.cv2.boundingRect(cnt)
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 3)
    if i<1:
        return True
    return False

def startReading(cap, H, seri, speed, dic):
    cntr = 0
    songStart, firstNote = False, True
    initCap = None
    last_song = ""
    while True:
        _, frame = cap.read()
        if frame is None:
            break
        if dic['Song'] != last_song:
            print("Current song: ", dic['Song'])
            last_song = dic['Song']
        frame = cv2.warpPerspective(frame, H, (720, 480))
        cntr += 1
        if cntr == 5 and songStart == False:
            if songReadyToBegin(frame, dic):                
                print("Start")
                # time.sleep(0.5)
                # _, frame = cap.read()
                # frame = cv2.warpPerspective(frame, H, (720, 480))
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                initCap = cv2.inRange(hsv_frame,(0,0,186), (179, 255, 255))
                initCap = initCap[140:194,118:619]
                if dic['Song'] == "":
                    print("* You havent enterd the song !!!")
                songStart = True
            cntr = 0
        
        elif songStart:            
            # Check the first note down
            if firstNoteDown(initCap, frame, dic):
                print("First Note")
                if dic['Test']:
                    time.sleep(5)
                if seri != None:
                    # Linear regression
                    time.sleep(-0.0164 * (speed - 3) + 1.3396) #41
                    play(seri, dic['File'][1], dic['File'][0])
                    
                songStart = False
            # if firstNote==False and checkSongEnd(frame):
            #     print("Song End")
            #     songStart, firstNote = False, True
        cv2.imshow("frame", frame)   
        # cv2.setMouseCallback("frame", getPos)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

def camera_main(args, dic):    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if (cap.isOpened()== False): 
        print("Error opening video stream or file")
    s = connectSerial()
    screen_pos = getScreenPos(cap)
    if screen_pos == None:
        cap.release()
        cv2.destroyAllWindows()
        return
    screen_pos = [screen_pos[0][0],screen_pos[1][1],screen_pos[2][2],screen_pos[3][3]]
    cv2.destroyAllWindows()
    H = cv2.getPerspectiveTransform(np.array(np.float32(screen_pos)), np.array(np.float32([[720, 0],[720, 480],[0,0],[0, 480]])))
    startReading(cap, H, s, args.speed, dic)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Camera')
    parser.add_argument('--scipt', type=str, default=name_of_song,
                        help='title of the script')
    parser.add_argument('--speed', type=str, default=speed_of_song,
                        help='speed of the song')
    args = parser.parse_args()
       
    manager = Manager()
    return_dict = manager.dict()
    return_dict['Song'] = args.scipt
    return_dict['File'] = ""
    return_dict['File'] = startDecoding(args.scipt)
    return_dict['Test'] = False
    proc = Process(target=camera_main, args=(args, return_dict))
    proc.start()
    time.sleep(3)

    file_path = os.path.dirname(os.path.realpath(__file__))
    
    while True:
        if not proc.is_alive():
            break
        song =  input('Enter New Song:\n')
        if song == "test":
            return_dict['Test'] = not return_dict['Test']
            if return_dict['Test']:
                print("Testing mode")
            else:
                print("Normal mode")
        elif len(song) >= 11:
            try:  
                f = open(file_path+'/File/'+song+'.txt', "r")
            except:
                print(song + '.txt does not exist')
                continue

            return_dict['Song'] = song
            return_dict['File'] = startDecoding(song)
        


    