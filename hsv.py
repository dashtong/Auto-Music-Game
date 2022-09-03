import cv2
import numpy as np


# cap = cv2.VideoCapture("C:\\Users\\OWNER\\Desktop\\test.mp4")

frame = cv2.imread("C:\\Users\\OWNER\\Desktop\\t.png")

if frame is None:
    print("Cant")
# cap = cv2.VideoCapture(0)

def nothing(x):
    pass
# Creating a window for later use
cv2.namedWindow('result')

# Starting with 100's to prevent error while masking
hL,sL,vL,hU,sU,vU = 100,100,100,179,255,255

# Creating track bar
cv2.createTrackbar('hL', 'result',0,179,nothing)
cv2.createTrackbar('hU', 'result',0,179,nothing)
cv2.createTrackbar('sL', 'result',0,255,nothing)
cv2.createTrackbar('sU', 'result',0,255,nothing)
cv2.createTrackbar('vL', 'result',0,255,nothing)
cv2.createTrackbar('vU', 'result',0,255,nothing)
cv2.setTrackbarPos('hL', 'result',15)
cv2.setTrackbarPos('sL', 'result',160)
cv2.setTrackbarPos('vL', 'result',65)
cv2.setTrackbarPos('hU', 'result',35)
cv2.setTrackbarPos('sU', 'result',255)
cv2.setTrackbarPos('vU', 'result',255)

# cv2.createTrackbar('rL', 'result',0,255,nothing)
# cv2.createTrackbar('rU', 'result',0,255,nothing)
# cv2.createTrackbar('gL', 'result',0,255,nothing)
# cv2.createTrackbar('gU', 'result',0,255,nothing)
# cv2.createTrackbar('bL', 'result',0,255,nothing)
# cv2.createTrackbar('bU', 'result',0,255,nothing)
# cv2.setTrackbarPos('rL', 'result',185)
# cv2.setTrackbarPos('gL', 'result',105)
# cv2.setTrackbarPos('bL', 'result',0)
# cv2.setTrackbarPos('rU', 'result',255)
# cv2.setTrackbarPos('gU', 'result',255)
# cv2.setTrackbarPos('bU', 'result',139)



x, y=  350, 245
w, h = 70*2, 85*2 

while(1):

    
#    tFrame = cv2.transpose(frame)
    # flipFrame = cv2.flip(frame, 0)
    flipFrame = frame[:]
    height, width, channels = flipFrame.shape 
    # cropFrame = frame

    cropFrame = cv2.resize(flipFrame, ((int)(width/2), (int)(height/2)))

    #converting to HSV
    hsv = cv2.cvtColor(cropFrame,cv2.COLOR_BGR2HSV)
    # rgb = cv2.cvtColor(cropFrame,cv2.COLOR_BGR2RGB)
    
    # get info from track bar and appy to result
    hL = cv2.getTrackbarPos('hL','result')
    sL = cv2.getTrackbarPos('sL','result')
    vL = cv2.getTrackbarPos('vL','result')
    hU = cv2.getTrackbarPos('hU','result')
    sU = cv2.getTrackbarPos('sU','result')
    vU = cv2.getTrackbarPos('vU','result')
    # rL = cv2.getTrackbarPos('rL','result')
    # gL = cv2.getTrackbarPos('gL','result')
    # bL = cv2.getTrackbarPos('bL','result')
    # rU = cv2.getTrackbarPos('rU','result')
    # gU = cv2.getTrackbarPos('gU','result')
    # bU = cv2.getTrackbarPos('bU','result')

    # Normal masking algorithm
    lower_blue = np.array([hL,sL,vL])
    upper_blue = np.array([hU,sU,vU])
    # lower_blue = np.array([rL,gL,bL])
    # upper_blue = np.array([rU,gU,bU])

    mask = cv2.inRange(hsv,lower_blue, upper_blue)
    # mask = cv2.inRange(rgb,lower_blue, upper_blue)

    result2 = cv2.bitwise_and(cropFrame,cropFrame,mask = mask)

    cv2.imshow('result2',result2)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break


cv2.destroyAllWindows()