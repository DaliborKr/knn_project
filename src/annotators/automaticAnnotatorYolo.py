import cv2
import numpy as np
import json
import argparse
import os
from ultralytics import YOLO
from os.path import basename, splitext


def load_image_paths_from_folder(folder):
    filenames = os.listdir(folder)
    paths = []
    for filename in filenames:
        paths.append(os.path.join(folder,filename))
    return paths

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
parser.add_argument("-m", "--model", help="Path to output YOLO model file", default="runs/detect/train/weights/best.pt")

args = parser.parse_args()


inputFolderPath = args.folder
output_path = args.output
model_path = args.model

model = YOLO(model_path)

images = load_image_paths_from_folder(inputFolderPath)


# Add metadata to annotations
img = cv2.imread(images[0])
data_height, data_width, _ = img.shape
annotations["metadata"]["frame_width"] = data_width
annotations["metadata"]["frame_height"] = data_height


for img in images:
    current_frame_name = splitext(basename(img))[0]

    results = model(img, max_det=1000, conf=0.50, iou=0.4, augment=False)

    for result in results:
        for box in result.boxes.data:
            x_min, y_min, x_max, y_max, confidence, class_id = box.tolist()
            x_min, y_min, x_max, y_max = map(int, [x_min, y_min, x_max, y_max])

            box = (x_min, y_min, x_max, y_max)
            annotations["frames"].setdefault(current_frame_name, []).append(box)


    print("Frame: '", current_frame_name, "' successfully annotated.", sep="")

with open(output_path, "w") as f:
    json.dump(annotations, f, indent=4)