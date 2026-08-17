"""Week 2 - Part 2: Capturing a video from the webcam.

Records continuously to myvideo.avi until the user presses 'q'.
"""

import cv2

cam = cv2.VideoCapture(0)  # create webcam object

fourcc = cv2.VideoWriter_fourcc(*'XVID')  # codec for AVI
out = cv2.VideoWriter('myvideo.avi', fourcc, 20.0, (640, 480))  # output file

if not cam.isOpened():
    print("not able to open computer camera")
    exit()
    

print("recording... press 'q' to stop")

while True:
    result, image = cam.read()
    if not result:
        print("Not able to capture frame (stream ending)")
    cv2.imshow('Captured Image', image)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()

cam.release()
