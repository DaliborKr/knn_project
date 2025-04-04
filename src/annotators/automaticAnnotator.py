import cv2
import numpy as np
import json
import argparse

annotations = {
    "metadata": {
        "frame_width": 0,
        "frame_height": 0,
        "fps": 0
    },
    "frames": {}
}

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", help="Path to input video", required=True)
parser.add_argument("-o", "--output", help="Path to output annotation file", default="annotations.json")
parser.add_argument("-int", "--interval", nargs=2, type=int, metavar=("START", "END"), help="Interval of chosen frames", default=[1, 9])

args = parser.parse_args()


video_path = args.video
output_path = args.output
start_frame = args.interval[0]
end_frame = args.interval[1]


cap = cv2.VideoCapture(video_path)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Add metadata to annotations
annotations["metadata"]["frame_width"] = frame_width
annotations["metadata"]["frame_height"] = frame_height
annotations["metadata"]["fps"] = fps



frame_count = 0

while cap.isOpened() and frame_count <= end_frame:
    if frame_count >= start_frame :
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


        _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)  # Adjust second argument if needed

        # Find contours of beetles
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if 50 < area < 400:  # Filter out very small or large objects
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Beetle", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                box = (x, y, x+w, y+h)
                annotations["frames"].setdefault(frame_count, []).append(box)
        print("Frame ", frame_count, " successfully annotated.", sep="")
    else:
        cap.read()

    frame_count += 1

with open(output_path, "w") as f:
    json.dump(annotations, f, indent=4)

cap.release()