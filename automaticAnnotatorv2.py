import cv2
import numpy as np
import json
import argparse
import os

def load_images_from_folder(folder):
    global filenames
    filenames = os.listdir(folder)
    images = []
    for filename in filenames:
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images

annotations = {
    "metadata": {
        "frame_width": 0,
        "frame_height": 0,
        "fps": 0
    },
    "frames": {}
}

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", help="Path to input folder", default="F:/datasets/dataset2 - kopie/train/images")
parser.add_argument("-o", "--output", help="Path to output annotation file", default="annoted/test.json")

args = parser.parse_args()


inputFolderPath = args.folder
output_path = args.output

current_frame = 0

images = load_images_from_folder(inputFolderPath)
current_frame_name = filenames[current_frame][:-4]
lastFrame = len(images) - 1

# Add metadata to annotations
data_height, data_width, _ = images[0].shape
annotations["metadata"]["frame_width"] = data_width
annotations["metadata"]["frame_height"] = data_height


for img in images:
    current_frame_name = filenames[current_frame][:-4]
    frame = images[current_frame].copy()

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
            annotations["frames"].setdefault(current_frame_name, []).append(box)
    print("Frame: '", current_frame_name, "' successfully annotated.", sep="")

    current_frame += 1

with open(output_path, "w") as f:
    json.dump(annotations, f, indent=4)