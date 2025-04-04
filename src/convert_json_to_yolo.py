import json
import os
import argparse
import re

# example usage: python convert_json_to_yolo.py -o cropImgTest/2/ -j testCropJson.json

parser = argparse.ArgumentParser()
parser.add_argument("-j", "--json", help="Path to input json", required=True)
parser.add_argument("-o", "--output", help="Path to output annotation file", default="annotations.json")

args = parser.parse_args()

def convert_json_to_yolo(json_path="annotated/d1_01.json", output_dir="labels/train", class_id=0):

    os.makedirs(output_dir, exist_ok=True)

    json_name = re.sub(r".*/([^/]+)\.json$", r"\1", json_path)

    with open(json_path, "r") as f:
        data = json.load(f)

    # Get image dimensions from metadata if available, otherwise use defaults
    if isinstance(data, dict):
        # Get dimensions from metadata if available
        if "metadata" in data and data["metadata"]:
            image_width = data["metadata"]["frame_width"]
            image_height = data["metadata"]["frame_height"]
        
        # Get frames data
        if "frames" in data:
            frames_data = data["frames"]

    for frame_tag, boxes in frames_data.items():
        yolo_lines = []
        for box in boxes:
            if isinstance(box, list) and len(box) == 4:
                x1, y1, x2, y2 = box
                x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)

                # Skip if box has zero width or height
                if x1 == x2 or y1 == y2:
                    continue

                center_x = (x1 + x2) / 2 / image_width
                center_y = (y1 + y2) / 2 / image_height
                width = (x2 - x1) / image_width
                height = (y2 - y1) / image_height

                yolo_lines.append(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}")
        # Save to file in YOLO format
        output_file = os.path.join(output_dir, f"{frame_tag}.txt")
        with open(output_file, "w") as f:
            f.write("\n".join(yolo_lines))

convert_json_to_yolo(json_path=args.json, output_dir=args.output)