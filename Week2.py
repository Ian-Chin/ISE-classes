"""Week 2 - Part 1: Capturing an image from the webcam.

Press 'c' to save the current frame to myimage.png.
Press 'q' to quit.
"""

import cv2

cam = cv2.VideoCapture(0)  # create webcam object

if not cam.isOpened():
    print("not able to open computer camera")
    exit()

while True:
    result, image = cam.read()  # start to capture frame by frame
    if not result:
        print("Not able to capture frame (stream ending)")
        break

    cv2.imshow('Captured Image', image)  # show the UI for us to see

    # unicode code of a specified character.
    # Read the key only ONCE per loop, otherwise the second waitKey()
    # consumes a different key press and 'q' is often missed.
    key = cv2.waitKey(1)
    if key == ord('c'):  # key press - c
        cv2.imwrite('myimage.png', image)
        print("saved myimage.png")
    elif key == ord('q'):  # key press - q
        break

# Release the camera (close) and destroy the windows AFTER the loop
cam.release()
cv2.destroyAllWindows()
