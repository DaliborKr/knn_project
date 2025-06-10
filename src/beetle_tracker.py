from collections import defaultdict

import cv2
import numpy as np
import json
import argparse
import os
import sys
import signal

from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", help="Path to input video", required=True)
parser.add_argument("-o", "--output", help="Save tracks to set directory", default=None)
parser.add_argument("-m", "--model", help="Path to detector model", required=True)
parser.add_argument("--show", help="Show detection in window", action="store_true")
parser.add_argument("--save_video", help="Save video to set directory", default=None)
parser.add_argument('--track_length', type=int, default=300, help='Set from how many previous frames should tracks be visible')

parser.add_argument("--botsort", help="Use botsort for tracking", action="store_true")
parser.add_argument("--bytetrack", help="Use bytetrack for tracking", action="store_true")

args = parser.parse_args()

video_name = os.path.basename(args.video).split('.')[0]

# Load the YOLO11 model
model = YOLO(args.model)

save_video = False
if (args.save_video != None):
    save_video_path = os.path.join(args.save_video, f"{video_name}_tracks.mp4")
    os.makedirs(os.path.dirname(save_video_path), exist_ok=True)
    save_video = True

video_path = args.video
cap = cv2.VideoCapture(video_path)

save_tracks = False
if (args.output != None):
    save_tracks_path = os.path.join(args.output, f"{video_name}_tracks.json")
    os.makedirs(os.path.dirname(save_tracks_path), exist_ok=True)
    save_tracks = True

# Store the track history
track_history = defaultdict(lambda: [])

tracks_all = {}
kill_signal = False

video_writer = None

current_frame = 0

show = args.show

if (args.bytetrack and not args.botsort): 
    tracker_path = os.path.join("tracker_configs", "bytetrack.yaml")
elif (args.botsort and not args.bytetrack):
    tracker_path = os.path.join("tracker_configs", "botsort.yaml")
else:
    exit("Choose one tracker --bytetrack or --botsort")

def signal_handler(sig, frame):
    global kill_signal
    kill_signal = True

signal.signal(signal.SIGINT, signal_handler)

# Loop through the video frames
while cap.isOpened() and not kill_signal:
    # Read a frame from the video
    success, frame = cap.read()
    print(f"Current frame: {current_frame}")

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, tracker=tracker_path, max_det=2000, conf=0.4, iou=0.5, imgsz=1920)

        # Get the boxes and track IDs
        boxes = results[0].boxes.xyxy.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()

        # Visualize the results on the frame
        annotated_frame = results[0].plot(labels=False, conf=False, color_mode="instance", line_width=2)
        # Plot the tracks
        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = box

            x1 = float(x1)
            y1 = float(y1)
            x2 = float(x2)
            y2 = float(y2)

            box = [x1, y1, x2, y2]

            tracks_all.setdefault(str(current_frame), {}).setdefault(str(track_id), []).append(box)

            track = track_history[track_id]

            track.append((float((x1 + x2) / 2), float((y1 + y2) / 2)))  # x, y center point
            if len(track) > args.track_length:  
                track.pop(0)

            # Draw the tracking lines
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=2)

        if (save_video):
            if video_writer is None:
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                height, width = annotated_frame.shape[:2]
                # Use 'mp4v' codec for .mp4 output
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(
                    save_video_path, 
                    fourcc, 
                    fps, 
                    (width, height)
                )
            video_writer.write(annotated_frame)

        # Display the annotated frame
        if (show): 
            cv2.imshow("YOLO11 Tracking", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    else:
        # Break the loop if the end of the video is reached
        break

    current_frame += 1

if (save_tracks):
    with open(save_tracks_path, "w") as f:
        json.dump(tracks_all, f, indent=4)
# Release the video capture object and close the display window

cap.release()
if video_writer is not None:
    video_writer.release()
if (show): cv2.destroyAllWindows()