import cv2
import HandTrackingModule as htm
import math
import numpy as np
from djitellopy import tello
import time

# Finding the face and hand and annotating the screen as output
def findFace(img):
    # For tello pilot finding
    faceArea = 0
    rectCentroid = [0, 0]
    faceClassifier = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceClassifier.detectMultiScale(grayImg, 1.2, 8)

    detector = htm.handDetector(detectionCon=0.8)
    img = detector.findHands(img)
    landmarkList = detector.findPosition(img, draw=False)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 4)
        rectCentroid = [x + w//2, y + h//2]
        faceArea = w*h
        cv2.putText(img, "PILOT RECOGNIZED", (x, y + 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
        if len(landmarkList)!=0:
            if(x-w-50) < landmarkList[0][1] < (x-60) and y < landmarkList[0][2] < (y+h):
                cv2.rectangle(img, (x - w - 50, y), (x - 60, y + h), (0, 255, 0), 4)
                cv2.putText(img, "HAND RECOGNIZED", (x - w - 50 + 10, y + 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
                gestureController()
            else:
                cv2.rectangle(img, (x - w - 50, y), (x - 60, y + h), (0, 0, 255), 4)
                cv2.putText(img, "PLACE HAND HERE", (x - w -50 + 10, y + 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
    return img, faceArea, rectCentroid


# Track face as a form of flight control
def trackFace(img, imgWidth, pidArray, pError, pErrorY, faceArea, rectCentroid):
    x = rectCentroid[0]
    y = rectCentroid[1]
    forwardSpeed = 0
    error = x - imgWidth // 2
    errorY = y - imgHeight // 2

    angularSpeed = pidArray[0]*error + pidArray[1]*(error-pError)
    angularSpeed = int(np.clip(angularSpeed, -30, 30))

    verticalSpeed = pidArray[0]*errorY + pidArray[1]*(errorY-pErrorY)
    verticalSpeed = int(np.clip(verticalSpeed, -20, 20))

    if 6800 < faceArea < 6200:
        forwardSpeed = 0
    elif faceArea > 6800:
        forwardSpeed = -20
    elif faceArea < 6200:
        forwardSpeed = 20

    if x == 0:
        verticalSpeed = 0
        forwardSpeed = 0
        error = 0

    droneInstance.send_rc_control(0, forwardSpeed, verticalSpeed, angularSpeed)
    return error, errorY


# Control flight using gestures
def gestureController():
    # 3. Recognize hand
    #   a. determine direction of hand and annotate screen (U/D || L/R)
    #   b. determine movement based on gesture (number of fingers up for given amount of time ~5 seconds)
    #       i. U/D[0 0 0 0] || L/R[1 1 1 1] is hold position
    #      vi. L/R[1 0 0 0] is left
    #     vii. L/R[0 1 1 1] is right
    #    viii. L/R[1 1 1 0] is rotate left
    #      ix. L/R[0 0 0 1] is rotate right
    detector = htm.handDetector()
    landmarkList = detector.findPosition(img, draw=False)
    if len(landmarkList) != 0:
        if landmarkList[4][2] < landmarkList[2][2]:
            print("looking up")




# Active and connect to drone
droneInstance = tello.Tello()
droneInstance.connect()

# find battery life of drone
print(droneInstance.get_battery())
droneInstance.streamon()
droneInstance.takeoff()
droneInstance.send_rc_control(0, 0, 20, 0)
time.sleep(3)
droneInstance.send_rc_control(0, 0, 0, 0)

prevTime, currTime = 0, 0
imgWidth, imgHeight = 360, 240

pidArray = [0.4, 0.4, 0]
pError = 0
pErrorY = 0
trackFaceBool = True

# main loop
# webcam = cv2.VideoCapture(1)
while True:
    # Webcam reading and finding face
    img = droneInstance.get_frame_read().frame
    # success, img = webcam.read()
    img = cv2.resize(img, (imgWidth, imgHeight))
    img, faceArea, rectCentroid = findFace(img)


    # Calculating and displaying frames per second
    currTime = time.time()
    fps = 1/(currTime - prevTime)
    prevTime = currTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 1)

    if cv2.waitKey(1) & 0xFF == ord('w'):
        trackFaceBool = not trackFaceBool

    if trackFaceBool:
        pError, pErrorY = trackFace(img, imgWidth, pidArray, pError, pErrorY, faceArea, rectCentroid)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        droneInstance.land()
        break
