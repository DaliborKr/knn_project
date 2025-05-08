from collections import defaultdict

import cv2
import numpy as np
import json

from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("runs/detect/train21/weights/best.pt")

video_name = "d3_01"

# Open the video file
video_path = f"BuoT/{video_name}.mp4"
cap = cv2.VideoCapture(video_path)

output_tracks_path = f"tracking_results_bytetrack/{video_name}.json"

# Store the track history
track_history = defaultdict(lambda: [])

tracks_all = {}

current_frame = 0

show = False

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    print(f"Current frame: {current_frame}")

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, tracker="bytetrack.yaml", max_det=2000, conf=0.4, iou=0.5, imgsz=1920)

        # Get the boxes and track IDs
        boxes = results[0].boxes.xyxy.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()

        # Visualize the results on the frame
        if (show): annotated_frame = results[0].plot(labels=False, conf=False, color_mode="instance", line_width=2)
        # Plot the tracks
        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = box

            x1 = float(x1)
            y1 = float(y1)
            x2 = float(x2)
            y2 = float(y2)

            box = [x1, y1, x2, y2]

            tracks_all.setdefault(str(current_frame), {}).setdefault(str(track_id), []).append(box)

            # tracks_all["ids"].setdefault(str(track_id), []).append({
            #     "frame": current_frame,
            #     "box": box            # convert tuple to list if needed for JSON
            # })

            track = track_history[track_id]

            track.append((float((x1 + x2) / 2), float((y1 + y2) / 2)))  # x, y center point
            if len(track) > 300:  # retain 30 tracks for 30 frames
                track.pop(0)

            # Draw the tracking lines
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            if (show): cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=2)

        # Display the annotated frame
        if (show): cv2.imshow("YOLO11 Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            with open(output_tracks_path, "w") as f:
                json.dump(tracks_all, f, indent=4)
            break
    else:
        # Break the loop if the end of the video is reached
        with open(output_tracks_path, "w") as f:
                json.dump(tracks_all, f, indent=4)
        break

    current_frame += 1

# Release the video capture object and close the display window
cap.release()
if (show): cv2.destroyAllWindows()