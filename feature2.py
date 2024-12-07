import cv2
import os
import numpy as np
from cvzone.HandTrackingModule import HandDetector

def run_presentation(folder_path):
    # Parameters
    width, height = 1280, 720
    gestureThreshold = 300

    # Camera Setup
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

    # Variables
    imgList = []
    delay = 30
    buttonPressed = False
    counter = 0
    imgNumber = 0
    annotations = [[]]
    annotationNumber = -1
    annotationStart = False
    hs, ws = int(140), int(250)  # Width and height of the small image preview

    # Load presentation images
    pathImages = sorted(os.listdir(folder_path), key=len)
    for path in pathImages:
        imgList.append(cv2.imread(os.path.join(folder_path, path)))

    if not imgList:
        print("No images found in the folder. Exiting.")
        return

    print(f"Loaded {len(imgList)} slides from {folder_path}")

    while True:
        # Get image frame from the webcam
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)  # Flip the webcam image
        pathFullImage = imgList[imgNumber]
        imgCurrent = pathFullImage.copy()

        # Detect hand and its landmarks
        hands, img = detectorHand.findHands(img)  # Draw hand landmarks

        # Draw the Gesture Threshold line
        cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

        if hands and buttonPressed is False:
            hand = hands[0]
            cx, cy = hand["center"]
            lmList = hand["lmList"]  # List of 21 Landmark points
            fingers = detectorHand.fingersUp(hand)  # Check which fingers are up

            # Constrain values for easier drawing
            xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
            yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
            indexFinger = xVal, yVal

            # Gesture for slide navigation
            if cy <= gestureThreshold:
                if fingers == [1, 0, 0, 0, 0]:  # Left swipe gesture
                    print("Left")
                    buttonPressed = True
                    if imgNumber > 0:
                        imgNumber -= 1
                        annotations = [[]]
                        annotationNumber = -1
                        annotationStart = False
                if fingers == [0, 0, 0, 0, 1]:  # Right swipe gesture
                    print("Right")
                    buttonPressed = True
                    if imgNumber < len(imgList) - 1:
                        imgNumber += 1
                        annotations = [[]]
                        annotationNumber = -1
                        annotationStart = False

            # Gesture for annotation (index and middle finger up)
            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)

            # Gesture to start annotation (only index finger up)
            if fingers == [0, 1, 0, 0, 0]:
                if annotationStart is False:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([])
                annotations[annotationNumber].append(indexFinger)
                cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            else:
                annotationStart = False

            # Gesture to remove the last annotation (3 fingers up)
            if fingers == [0, 1, 1, 1, 0]:
                if annotations:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True

        # Reset button press delay
        if buttonPressed:
            counter += 1
            if counter > delay:
                counter = 0
                buttonPressed = False

        # Draw stored annotations on the slide
        for i, annotation in enumerate(annotations):
            for j in range(len(annotation)):
                if j != 0:
                    cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 255), 12)

        # Add webcam preview in the top-right corner
        imgSmall = cv2.resize(img, (ws, hs))
        h, w, _ = imgCurrent.shape
        imgCurrent[0:hs, w - ws: w] = imgSmall

        # Display images
        cv2.imshow("Slides", imgCurrent)
        cv2.imshow("Image", img)

        key = cv2.waitKey(1)
        if key == ord('q'):  # Quit the application
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    folder_path = "./uploads/presentation_folder"
    run_presentation(folder_path)
