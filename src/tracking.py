from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("runs\\detect\\train21\\weights\\best.pt")

# Open the video file
video_path = "BuoT\\d4_01.mp4"
cap = cv2.VideoCapture(video_path)

# Initialize VideoWriter (we'll set parameters after reading the first frame)
video_writer = None

# Store the track history
track_history = defaultdict(lambda: [])

counter = 0
# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame
        results = model.track(
            frame, 
            persist=True, 
            tracker="botsort.yaml", 
            max_det=2000, 
            conf=0.4, 
            iou=0.5, 
            imgsz=1920
        )

        # Get the boxes and track IDs
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()

        # Visualize the results
        annotated_frame = results[0].plot(
            labels=False, 
            conf=False, 
            color_mode="instance", 
            line_width=1
        )

        # Plot the tracks
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y center point
            if len(track) > 300:  # retain 300 track points
                track.pop(0)

            # Draw the tracking lines
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(
                annotated_frame, 
                [points], 
                isClosed=False, 
                color=(230, 230, 230), 
                thickness=1
            )

        # Initialize VideoWriter with first frame's properties
        if video_writer is None:
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            height, width = annotated_frame.shape[:2]
            # Use 'mp4v' codec for .mp4 output (adjust if needed)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(
                'output_video.mp4', 
                fourcc, 
                fps, 
                (width, height)
            )
        
        # Write frame to video
        video_writer.write(annotated_frame)

        # Display the annotated frame
        # cv2.imshow("YOLO11 Tracking", annotated_frame)
        counter += 1
        if (counter > 300):
            break

        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break  # Exit if video ends

# Cleanup
cap.release()
if video_writer is not None:
    video_writer.release()
cv2.destroyAllWindows()