import cv2
import json
import argparse
import os
import numpy as np

# python src/annotators/annotatorVideoWin.py -v splitted/test1/d2_01_120-159.mp4 -o ground_truth_tracks/gt_test1.json -i ground_truth_tracks/gt_test1.json

annotations = {
    "metadata": {
        "frame_width": 0,
        "frame_height": 0,
        "fps": 0
    },
    "frames": {}
}

drawing = False
start_x, start_y = -1, -1
current_frame = 0
hovered_box = None
boxesVisible = True

# Zoom/pan variables
panning = False
start_pan_x, start_pan_y = 0, 0
offset_x, offset_y = 0.0, 0.0
scale = 1.0
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

inputVideoPath = ""
inputAnnotationPath = ""
outputAnnotationPath = ""
xCurrent, yCurrent = 0, 0
firstFrame, lastFrame = 0, 0

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", help="Path to input video file", required=True)
parser.add_argument("-i", "--input", help="Path to input annotation file", default="annotations.json")
parser.add_argument("-o", "--output", help="Path to output annotation file", default="annotations.json")

def clip_to_bounds(x1, y1, x2, y2, width, height):
    return max(0, min(x1, width)), max(0, min(y1, height)), max(0, min(x2, width)), max(0, min(y2, height))

def draw_boxes(frame, boxes):
    global scale, offset_x, offset_y
    # Precompute commonly used values
    roi_x1 = int(max(0, offset_x))
    roi_y1 = int(max(0, offset_y))
    roi_width, roi_height = frame.shape[1], frame.shape[0]  # Image width and height

    if boxesVisible:
        for box in boxes:
            x1, y1, x2, y2 = box
            # Convert to display coordinates
            display_x1 = int((x1 - roi_x1) * scale)
            display_y1 = int((y1 - roi_y1) * scale)
            display_x2 = int((x2 - roi_x1) * scale)
            display_y2 = int((y2 - roi_y1) * scale)
            
            # Clip coordinates to the visible area in the window
            display_x1, display_y1, display_x2, display_y2 = clip_to_bounds(display_x1, display_y1, display_x2, display_y2, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            # Set color based on hovered box status
            color = (0, 255, 0) if box != hovered_box else (0, 0, 255)
            
            # Draw box if valid (ensure positive area)
            if display_x2 > display_x1 and display_y2 > display_y1:
                cv2.rectangle(frame, (display_x1, display_y1), (display_x2, display_y2), color, 2)
    
    # Drawing in progress
    if drawing:
        # Convert drawing coordinates to display scale
        display_start_x = int((start_x - roi_x1) * scale)
        display_start_y = int((start_y - roi_y1) * scale)
        display_end_x = int((xCurrent / scale + offset_x - roi_x1) * scale)
        display_end_y = int((yCurrent / scale + offset_y - roi_y1) * scale)
        
        # Draw the ongoing rectangle in blue
        cv2.rectangle(frame, (display_start_x, display_start_y), (display_end_x, display_end_y), (255, 0, 0), 2)
    
    return frame 

def mouse_events(event, x, y, flags, param):
    global start_x, start_y, drawing, hovered_box, panning, offset_x, offset_y, scale
    global start_pan_x, start_pan_y, xCurrent, yCurrent
    
    xCurrent, yCurrent = x, y
    original_width = annotations["metadata"]["frame_width"]
    original_height = annotations["metadata"]["frame_height"]
    
    if event == cv2.EVENT_MOUSEMOVE:
        if not drawing and not panning:
            hovered_box = None
            original_x = x / scale + offset_x
            original_y = y / scale + offset_y
            for box in annotations["frames"].get(frameName, []):
                x1, y1, x2, y2 = box
                if x1 <= original_x <= x2 and y1 <= original_y <= y2:
                    hovered_box = box
                    break

    elif event == cv2.EVENT_LBUTTONDOWN:
        panning = True
        start_pan_x, start_pan_y = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        panning = False

    elif event == cv2.EVENT_MOUSEWHEEL:
        zoom_center_x = x / scale + offset_x
        zoom_center_y = y / scale + offset_y
        
        if flags > 0:
            new_scale = scale * 1.1
        else:
            new_scale = scale / 1.1
        
        new_scale = max(0.1, min(new_scale, 10.0))
        offset_x = zoom_center_x - (x / new_scale)
        offset_y = zoom_center_y - (y / new_scale)
        offset_x = max(0, min(offset_x, original_width - WINDOW_WIDTH/new_scale))
        offset_y = max(0, min(offset_y, original_height - WINDOW_HEIGHT/new_scale))
        scale = new_scale
    
    if event == cv2.EVENT_MOUSEMOVE and panning:
        delta_x = x - start_pan_x
        delta_y = y - start_pan_y
        offset_x -= delta_x / scale 
        offset_y -= delta_y / scale 
        # Apply boundaries
        max_x_offset = original_width - (WINDOW_WIDTH/scale)
        max_y_offset = original_height - (WINDOW_HEIGHT/scale)
        offset_x = max(0, min(offset_x, max_x_offset))
        offset_y = max(0, min(offset_y, max_y_offset))
        
        start_pan_x, start_pan_y = x, y

def on_trackbar(val):
    global current_frame
    current_frame = max(firstFrame, min(val, lastFrame))
    cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame)

def parseArgs():
    global inputVideoPath, inputAnnotationPath, outputAnnotationPath, firstFrame, lastFrame, current_frame
    args = parser.parse_args()
    inputVideoPath = args.video
    outputAnnotationPath = args.output
    inputAnnotationPath = args.input

parseArgs()

# Initialize video capture
video_capture = cv2.VideoCapture(inputVideoPath)
if not video_capture.isOpened():
    print(f"Error opening video file {inputVideoPath}")
    exit(1)

# Get video properties
original_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
original_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video_capture.get(cv2.CAP_PROP_FPS)
lastFrame = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) - 1

annotations["metadata"]["frame_width"] = original_width
annotations["metadata"]["frame_height"] = original_height
annotations["metadata"]["fps"] = fps

cv2.namedWindow("Video Annotator", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Video Annotator", WINDOW_WIDTH, WINDOW_HEIGHT)
cv2.createTrackbar("Seek", "Video Annotator", firstFrame, lastFrame, on_trackbar)
cv2.setMouseCallback("Video Annotator", mouse_events)

# Load existing annotations
try:
    with open(inputAnnotationPath, "r") as f:
        loaded_annotations = json.load(f)
        annotations.update(loaded_annotations)
    print("Annotations loaded!")
except FileNotFoundError:
    print("No saved annotations found.")

while True:
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    ret, frame = video_capture.read()
    if not ret:
        print("Error reading frame")
        break

    frameName = str(current_frame)
    if frame is None:
        print(f"Error: Invalid frame at index {current_frame}")
        continue

    # Calculate visible region
    roi_width = WINDOW_WIDTH / scale
    roi_height = WINDOW_HEIGHT / scale
    roi_x1 = int(max(0, offset_x))
    roi_y1 = int(max(0, offset_y))
    roi_x2 = int(min(original_width, offset_x + roi_width))
    roi_y2 = int(min(original_height, offset_y + roi_height))

    if roi_x2 > roi_x1 and roi_y2 > roi_y1:
        roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
        resized_roi = cv2.resize(roi, (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation=cv2.INTER_NEAREST)
    else:
        resized_roi = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)

    display_frame = draw_boxes(resized_roi, annotations["frames"].get(frameName, []))
    cv2.imshow("Video Annotator", display_frame)

    key = cv2.waitKey(30)

    if key == ord("x"):
        break
    elif key == ord("q"):
        if hovered_box:
            annotations["frames"][frameName].remove(hovered_box)
            if not annotations["frames"][frameName]:
                del annotations["frames"][frameName]
            hovered_box = None
    elif key == ord("e"):
        if not drawing:
            drawing = True
            start_x = xCurrent / scale + offset_x
            start_y = yCurrent / scale + offset_y
        else:
            drawing = False
            end_x = xCurrent / scale + offset_x
            end_y = yCurrent / scale + offset_y
            if abs(end_x - start_x) > 5 and abs(end_y - start_y) > 5:
                box = (int(min(start_x, end_x)), int(min(start_y, end_y)),
                        int(max(start_x, end_x)), int(max(start_y, end_y)))
                annotations["frames"].setdefault(frameName, []).append(box)
    elif key == ord("d") and current_frame < lastFrame:
        current_frame += 1
        cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)
    elif key == ord("a") and current_frame > firstFrame:
        current_frame -= 1
        cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)
    elif key == ord("s"):
        #cv2.imwrite(f"images/train/frame_{current_frame}.jpg", frame)
        with open(outputAnnotationPath, "w") as f:
            json.dump(annotations, f, indent=4)
        print("Annotations saved!")
    elif key == ord("r"):
        boxesVisible = not boxesVisible

video_capture.release()
cv2.destroyAllWindows()