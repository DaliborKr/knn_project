import cv2
import json
import argparse
import os

annotations = {
    "metadata": {
        "frame_width": 0,
        "frame_height": 0,
        "fps": 0
    },
    "frames": {}
}  # Dictionary to store video metadata and bounding boxes per frame

drawing = False
start_x, start_y = -1, -1
current_frame = 0
hovered_box = None  # Tracks which box the mouse is hovering over

boxesVisible = True

inputVideoPath = ""
inputAnnotationPath = ""
outputAnnotationPath = ""

xCurrent = 0
yCurrent = 0

firstFrame = 0
lastFrame = 0

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", help="Path to input video", required=True)
parser.add_argument("-i", "--input", help="Path to input annotation file", default="def.json")
parser.add_argument("-o", "--output", help="Path to output annotation file", default="annotations.json")
parser.add_argument("-int", "--interval", nargs=2, type=int, metavar=("START", "END"), help="Interval of chosen frames", default=[0, 9])

# Function to draw bounding boxes
def draw_boxes(frame, boxes):
    if boxesVisible:
        for box in boxes:
            x1, y1, x2, y2 = box
            color = (0, 255, 0) if box != hovered_box else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    if drawing:
        cv2.rectangle(frame, (start_x, start_y), (xCurrent, yCurrent), (255, 0, 0), 1)
    return frame

def mouse_events(event, x, y, flags, param):
    global start_x, start_y, drawing, annotations, current_frame, hovered_box, xCurrent, yCurrent

    xCurrent, yCurrent = x, y

    if event == cv2.EVENT_MOUSEMOVE:
        if not drawing:
            hovered_box = None
            for box in annotations["frames"].get(str(current_frame), []):
                x1, y1, x2, y2 = box
                if x1 < x < x2 and y1 < y < y2:
                    hovered_box = box

def on_trackbar(val):
    global current_frame
    if val >= firstFrame and val <= lastFrame:
        current_frame = val
    else:
        current_frame = firstFrame if val < firstFrame else lastFrame
    cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)

def parseArgs():
    global inputVideoPath, inputAnnotationPath ,outputAnnotationPath, firstFrame, lastFrame, current_frame

    args = parser.parse_args()

    inputVideoPath = args.video
    outputAnnotationPath = args.output
    inputAnnotationPath = args.input
    firstFrame = args.interval[0]
    current_frame = firstFrame
    lastFrame = args.interval[1]

parseArgs()

# Load video
cap = cv2.VideoCapture(inputVideoPath)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

if not cap.isOpened():
    print("No video file '", inputVideoPath, "' found.", sep="")
    exit()

# Set window
cv2.namedWindow("Video Annotator", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Video Annotator", 1600, 900)

cv2.createTrackbar("Seek", "Video Annotator", firstFrame ,total_frames - 1 , on_trackbar)

cv2.setMouseCallback("Video Annotator", mouse_events)


cap = cv2.VideoCapture(inputVideoPath)

# Get video properties and add to metadata
annotations["metadata"]["frame_width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
annotations["metadata"]["frame_height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
annotations["metadata"]["fps"] = int(cap.get(cv2.CAP_PROP_FPS))

try:
    with open(inputAnnotationPath, "r") as f:
        loaded_annotations = json.load(f)
        # Handle both new and old format
    if "frames" in loaded_annotations:
        annotations["frames"] = {k: v for k, v in loaded_annotations["frames"].items()}
        # Keep metadata from loaded file if available
        if "metadata" in loaded_annotations:
            annotations["metadata"] = loaded_annotations["metadata"]
    else:
        # Convert old format to new format
        annotations["frames"] = {str(k): v for k, v in loaded_annotations.items() if k not in ["metadata"]}
    
    print("Annotations loaded!")
except:
    print("No saved annotations found.")

while cap.isOpened():
    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    ret, frame = cap.read()
    origin_frame = frame.copy()
    if not ret:
        break

    frame = draw_boxes(frame, annotations["frames"].get(str(current_frame), []))
    cv2.imshow("Video Annotator", frame)

    key = cv2.waitKey(30)

    if key == ord("x"):  # Quit
        break
    elif key == ord("q"):
        if drawing:
            drawing = False
        elif hovered_box:
            annotations["frames"][str(current_frame)].remove(hovered_box)
            if not annotations["frames"][str(current_frame)]:  # Remove empty frame entries
                del annotations["frames"][str(current_frame)]
            hovered_box = None
    elif key == ord("e"):
        if not drawing:
            drawing = True
            start_x, start_y = xCurrent, yCurrent
        else:
            drawing = False
            end_x, end_y = xCurrent, yCurrent
            if abs(end_x - start_x) > 5 and abs(end_y - start_y) > 5:  # Prevent tiny boxes
                box = (min(start_x, end_x), min(start_y, end_y), max(start_x, end_x), max(start_y, end_y))
                annotations["frames"].setdefault(str(current_frame), []).append(box)
    elif key == ord("d") and current_frame < lastFrame:  # Next frame
        current_frame += 1
        cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)
    elif key == ord("a") and current_frame > firstFrame:  # Previous frame
        current_frame -= 1
        cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)
    elif key == ord("s"):  # Save annotations
        # Save frame as image
        cv2.imwrite(f"images/train/frame_{current_frame}.jpg", origin_frame)
        with open(outputAnnotationPath, "w") as f:
            json.dump(annotations, f, indent=4)
        print("Annotations saved!")
    elif key == ord("r"):  # Makes visible/invisible other boxes
        boxesVisible = not boxesVisible

cap.release()
cv2.destroyAllWindows()