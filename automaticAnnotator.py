import cv2
import numpy as np
import json

annotations = {}

video_path = "2024_03_01-11_00_01.mp4"
cap = cv2.VideoCapture(video_path)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = int(cap.get(cv2.CAP_PROP_FPS))

output_path = "beetles_annotated2.mp4"
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

frame_count = 0 # init frame

while cap.isOpened() and frame_count < 100:
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
            annotations.setdefault(frame_count, []).append(box)


    out.write(frame)


    cv2.imshow("Beetle Annotation", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    frame_count += 1

with open("annotations.json", "w") as f:
    json.dump(annotations, f, indent=4)

cap.release()
out.release()
cv2.destroyAllWindows()