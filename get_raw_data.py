import cv2
import time
import numpy as np
import os
import argparse
from decode import startDecoding

# =============================================================================
# Initailizing variable
# =============================================================================
song_name = 'WindBlow_22_75' #'SilentMaj_Normal_10_75'#'10Pool_Master_75'
script_name = 'WindBlow_22_75' #'SilentMaj_Normal_10_75'#'10Pool_Master_75'
song_line = 'all'

# =============================================================================
framePositionSample = {
### positionName, (positionX, positionY, upperX, upperY, w, h, positionValue) ###   
        "y1": ( 630,  440, 490,  700, 70, 85, 10),
        "y2": ( 630,  680, 490,  840, 70, 85, 20),
        "y3": ( 630,  920, 490,  920, 70, 85, 30),
        "y4": ( 630, 1160, 490, 1150, 70, 85, 40),
        "y5": ( 630, 1390, 490, 1390, 70, 85, 50)
}

storage = [
        {'colorNameInLastFrame': '', 'colorInLastFrame': 0, 'green': False, 'greenStart': 0, 'greenEnd': 0, 'printedGreen': True, 'special': False},
        {'colorNameInLastFrame': '', 'colorInLastFrame': 0, 'green': False, 'greenStart': 0, 'greenEnd': 0, 'printedGreen': True, 'special': False},
        {'colorNameInLastFrame': '', 'colorInLastFrame': 0, 'green': False, 'greenStart': 0, 'greenEnd': 0, 'printedGreen': True, 'special': False},
        {'colorNameInLastFrame': '', 'colorInLastFrame': 0, 'green': False, 'greenStart': 0, 'greenEnd': 0, 'printedGreen': True, 'special': False},
        {'colorNameInLastFrame': '', 'colorInLastFrame': 0, 'green': False, 'greenStart': 0, 'greenEnd': 0, 'printedGreen': True, 'special': False}
]

colorBoundaries_ = {            
            "red":    ([170,130,175], [179,255,255], 2, 7),
            "blue":   ([100,180,170], [115,255,255], 3, 8),
            "orange": ([ 15,100,100], [ 20,255,255], 4, 9),                  
            "pink":   ([155,110,175], [160,255,255], 1, 6),    
            "green":  ([ 40,120,170], [ 95,230,220], 5, 6),           
}

colorBoundaries_hold = {            
            "green":  ([ 40,120,170], [ 95,230,220], 5, 6),   
            "red":    ([170,130,175], [179,255,255], 2, 7),
            "blue":   ([100,180,170], [115,255,255], 3, 8),
            "orange": ([ 15,100,100], [ 20,255,255], 4, 9),                  
            "pink":   ([155,110,175], [160,255,255], 1, 6),            
}

initial_cropped_frame = []
checkPos = 10

def pre_process_frame(frame):
    # # Rotate Every frame 90 anti-clockwise
    # frame = cv2.transpose(frame)
    # flipFrame = cv2.flip(frame, 90)
    # flipFrame = cv2.flip(frame, 0)
    return frame

def getFirstFrame(cap, framePosition):
    _, frame = cap.read()
    for _, (positionX, positionY, _, _, w, h, _) in framePosition.items():      
        initial_cropped_frame.append(frame[positionX:positionX+w, positionY:positionY+h])

def startAnalysing(s_n, s_l):
    bf = 1
    file_path = os.path.dirname(os.path.realpath(__file__))
    mp4Path = file_path+'/Video/'+s_n
    start_time = time.time()
    colorBoundaries = colorBoundaries_
    numofFrame = 1
# =============================================================================
# Preprocess chosen lines
# =============================================================================
    framePosition = {} 
    if s_l == 'all':
        framePosition = framePositionSample
    else:
        for i in [int(i)-1 for i in set(s_l)]:
            framePosition[list(framePositionSample)[i]] = framePositionSample[list(framePositionSample)[i]]

# =============================================================================
# Open files
# =============================================================================
    cap = cv2.VideoCapture(mp4Path+'.mov')
    if (cap.isOpened()== False): 
        cap = cv2.VideoCapture(mp4Path+'.mp4')
        if (cap.isOpened()== False): 
            print("Error opening video stream or file")
            return
    getFirstFrame(cap, framePosition)

    # Open a text file for recording
    if s_l == 'all':
        f = open(file_path+'/File/'+s_n+'.txt',"w")
    else:
        f = open(file_path+'/File/'+s_n+'_y'+s_l+'.txt',"w")

# =============================================================================
# Start the video
# =============================================================================
    buf = "  Start Analysing  "
    print("="*len(buf)+'\n'+buf+'\n'+"="*len(buf))

    while True:
        _, frame = cap.read()
        if frame is None:
            break
        frame = pre_process_frame(frame)
        height, width, _ = frame.shape
        smallFrame = cv2.resize(frame, ((int)(width/2), (int)(height/2)))   
        # frame = cv2.GaussianBlur(frame,(5,5),0)
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for pos_cnt, (_, (positionX, positionY, _, _, w, h, positionValue)) in enumerate(framePosition.items()):  
            cropFrame = frame[positionX:positionX+w, positionY:positionY+h]  
            # cropFrame[ np.sum(cropFrame, axis=2) > 180*3] = 0
            frame_diff = cropFrame - initial_cropped_frame[pos_cnt]
            frame_diff = np.sum(frame_diff, axis=2)
            frame_diff[frame_diff<100] = 0
            p_positionValue = int(positionValue / 10) - 1
            if np.count_nonzero(frame_diff) / (w*h) >= 0.92:
                if storage[p_positionValue]['green']:
                    colorBoundaries = colorBoundaries_hold
                else:
                    colorBoundaries = colorBoundaries_
                for colorName, (lower, upper, printValue, valueAfterGreen) in colorBoundaries.items():
        #            create NumPy arrays from the boundaries
                    lower = np.array(lower, dtype = np.uint8)
                    upper = np.array(upper, dtype = np.uint8)       
        #            fund the colors within the specified boundaries and apply the mask
                    mask = cv2.inRange(hsvFrame,lower, upper)             
                    cropMask = mask[positionX:positionX+w, positionY:positionY+h]
        #            Mask will be 0 when it is black
                    if cropMask.any() != 0:                               
        #            Ensure output is not Continuous
                        
                        if storage[p_positionValue]['green'] and storage[p_positionValue]['colorNameInLastFrame'] == 'green' and colorName != 'green':
                            if numofFrame - storage[p_positionValue]['greenStart'] <= (int)(bf/2):
                                    print("This is not a Block\t", positionValue+5)
                                    f.write(str(positionValue+5)+" F\n")
                            else:
                                if positionValue == checkPos:
                                    print("green End with diff color\t", f"{colorName}\t", positionValue+valueAfterGreen, ":\t", numofFrame)             
                                f.write(str(positionValue+valueAfterGreen) + " " + str(numofFrame) + "\n")
                            storage[p_positionValue]['printedGreen'] = True
                            storage[p_positionValue]['green'] = False

                        elif numofFrame - storage[p_positionValue]['colorInLastFrame'] > 1:
                            if positionValue == checkPos:
                                print(f"{colorName}\t", positionValue+printValue, ":\t", numofFrame)             
                            f.write(str(positionValue+printValue) + " " + str(numofFrame) + "\n")
                            if colorName == 'green' and storage[p_positionValue]['green'] == False:      
                                storage[p_positionValue]['green'] = True
                                storage[p_positionValue]['greenStart'] = numofFrame
                                
                        storage[p_positionValue]['colorNameInLastFrame'] = colorName
                        storage[p_positionValue]['colorInLastFrame'] = numofFrame                        
                        break

                # Special is Here
                if numofFrame != storage[p_positionValue]['colorInLastFrame'] and storage[p_positionValue]['green']==False:
                    print("Special\t", positionValue+1, ":\t", numofFrame)             
                    f.write(str(positionValue+1) + " " + str(numofFrame) + "\n")
                elif numofFrame != storage[p_positionValue]['colorInLastFrame'] and storage[p_positionValue]['green']:
                    print("green End with diff color\t", "Special\t", positionValue+6, ":\t", numofFrame)             
                    f.write(str(positionValue+6) + " " + str(numofFrame) + "\n")
                    storage[p_positionValue]['printedGreen'] = True
                    storage[p_positionValue]['green'] = False
                storage[p_positionValue]['colorInLastFrame'] = numofFrame    
            else:                    
        #            Check if green color long blocks end
                if storage[p_positionValue]['green']:
                    storage[p_positionValue]['greenEnd'] = numofFrame
                    storage[p_positionValue]['green'] = False
        #                A block has around 10 frame, but a line doesnt
                    if (storage[p_positionValue]['greenEnd'] - storage[p_positionValue]['greenStart']) < bf:
                        print("This is not a Block 1\t", positionValue+5, storage[p_positionValue]['greenEnd'] - storage[p_positionValue]['greenStart'])
                        f.write(str(positionValue+5)+" F\n")
                        break       
                    storage[p_positionValue]['printedGreen'] = False
                    
                
                if numofFrame == storage[p_positionValue]['greenEnd'] + bf:
                    if storage[p_positionValue]['printedGreen'] == False:
                        if positionValue == checkPos:
                            print("green End with green\t", "green", positionValue+6, ":\t", numofFrame-int(bf))
                        f.write(str(positionValue+6) + " " + str(numofFrame-int(bf)) + "\n")
                        storage[p_positionValue]['printedGreen'] = True
            cropMask = cv2.inRange(hsvFrame,np.array([155,110,175], dtype = np.uint8), np.array([160,255,255], dtype = np.uint8))[positionX:positionX+w, positionY:positionY+h]
            if positionValue == checkPos:
                cv2.imshow('cropFrame', cropFrame)
        cv2.imshow('cropMask', cropMask)
        cv2.imshow('frame', smallFrame)
        numofFrame += 1
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        
    timeCost = time.time() - start_time
    fps_ = numofFrame/timeCost
    fps = cap.get(cv2.CAP_PROP_FPS)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = length/fps
    
    print("Number of Frame:\n", numofFrame)
    print("Time Cost:\n", timeCost)
    print("FPS:\n", fps_)
    print("Video duration:\n", duration)
    f.write(str(numofFrame)+"\n"+str(duration))

    f.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Project 1')
    parser.add_argument("--line", "-l", type=str, default=song_line,
                        help="Line to detect")
    parser.add_argument('--song', "-s", type=str, default=song_name,
                        help='Name of the song file(without .mov)')
    parser.add_argument('--script', "-sc", type=str, default=script_name,
                        help='Name of the script, cannot include japanese')
    args = parser.parse_args()

    startAnalysing(args.song, args.line)