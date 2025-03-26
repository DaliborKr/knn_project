import cv2
import json
import argparse
import os
import numpy as np

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
parser.add_argument("-v", "--video", help="Path to input video", required=True)
parser.add_argument("-i", "--input", help="Path to input annotation file", default="def.json")
parser.add_argument("-o", "--output", help="Path to output annotation file", default="annotations.json")
parser.add_argument("-int", "--interval", nargs=2, type=int, metavar=("START", "END"), help="Interval of chosen frames", default=[0, 9])

def draw_boxes(frame, boxes):
    global scale, offset_x, offset_y
    
    # Calculate visible area in original coordinates
    roi_x1 = max(0, int(offset_x))
    roi_y1 = max(0, int(offset_y))
    
    if boxesVisible:
        for box in boxes:
            x1, y1, x2, y2 = box
            # Convert to display coordinates
            display_x1 = int((x1 - roi_x1) * scale)
            display_y1 = int((y1 - roi_y1) * scale)
            display_x2 = int((x2 - roi_x1) * scale)
            display_y2 = int((y2 - roi_y1) * scale)
            
            # Clip coordinates to visible area
            display_x1 = max(0, min(display_x1, WINDOW_WIDTH))
            display_y1 = max(0, min(display_y1, WINDOW_HEIGHT))
            display_x2 = max(0, min(display_x2, WINDOW_WIDTH))
            display_y2 = max(0, min(display_y2, WINDOW_HEIGHT))
            
            color = (0, 255, 0) if box != hovered_box else (0, 0, 255)
            if display_x2 > display_x1 and display_y2 > display_y1:
                cv2.rectangle(frame, (display_x1, display_y1), (display_x2, display_y2), color, 2)
    
    if drawing:
        # Convert drawing coordinates
        display_start_x = int((start_x - roi_x1) * scale)
        display_start_y = int((start_y - roi_y1) * scale)
        display_end_x = int((xCurrent / scale + offset_x - roi_x1) * scale)
        display_end_y = int((yCurrent / scale + offset_y - roi_y1) * scale)
        
        cv2.rectangle(frame, (display_start_x, display_start_y),
                     (display_end_x, display_end_y), (255, 0, 0), 2)
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
            for box in annotations["frames"].get(str(current_frame), []):
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
    if firstFrame <= val <= lastFrame:
        current_frame = val
    else:
        current_frame = firstFrame if val < firstFrame else lastFrame
    cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)

def parseArgs():
    global inputVideoPath, inputAnnotationPath, outputAnnotationPath, firstFrame, lastFrame, current_frame
    args = parser.parse_args()
    inputVideoPath = args.video
    outputAnnotationPath = args.output
    inputAnnotationPath = args.input
    firstFrame = args.interval[0]
    current_frame = firstFrame
    lastFrame = args.interval[1]

parseArgs()

cap = cv2.VideoCapture(inputVideoPath)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

if not cap.isOpened():
    print(f"No video file '{inputVideoPath}' found.")
    exit()

cv2.namedWindow("Video Annotator", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Video Annotator", WINDOW_WIDTH, WINDOW_HEIGHT)
cv2.createTrackbar("Seek", "Video Annotator", firstFrame, total_frames-1, on_trackbar)
cv2.setMouseCallback("Video Annotator", mouse_events)

annotations["metadata"]["frame_width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
annotations["metadata"]["frame_height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
annotations["metadata"]["fps"] = int(cap.get(cv2.CAP_PROP_FPS))

try:
    with open(inputAnnotationPath, "r") as f:
        loaded_annotations = json.load(f)
        if "frames" in loaded_annotations:
            annotations["frames"] = loaded_annotations["frames"]
            if "metadata" in loaded_annotations:
                annotations["metadata"] = loaded_annotations["metadata"]
        else:
            annotations["frames"] = {str(k): v for k, v in loaded_annotations.items()}
    print("Annotations loaded!")
except:
    print("No saved annotations found.")

original_width = annotations["metadata"]["frame_width"]
original_height = annotations["metadata"]["frame_height"]

while cap.isOpened():
    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    ret, frame = cap.read()
    if not ret:
        break

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

    display_frame = draw_boxes(resized_roi, annotations["frames"].get(str(current_frame), []))
    cv2.imshow("Video Annotator", display_frame)

    key = cv2.waitKey(30)

    if key == ord("x"):
        break
    elif key == ord("q"):
        if hovered_box:
            annotations["frames"][str(current_frame)].remove(hovered_box)
            if not annotations["frames"][str(current_frame)]:
                del annotations["frames"][str(current_frame)]
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
                annotations["frames"].setdefault(str(current_frame), []).append(box)
    elif key == ord("d") and current_frame < lastFrame:
        current_frame += 1
        cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)
    elif key == ord("a") and current_frame > firstFrame:
        current_frame -= 1
        cv2.setTrackbarPos("Seek", "Video Annotator", current_frame)
    elif key == ord("s"):
        cv2.imwrite(f"images/train/frame_{current_frame}.jpg", frame)
        with open(outputAnnotationPath, "w") as f:
            json.dump(annotations, f, indent=4)
        print("Annotations saved!")
    elif key == ord("r"):
        boxesVisible = not boxesVisible

cap.release()
cv2.destroyAllWindows()