import cv2
import os
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", help="Path to input video", required=True)
parser.add_argument("-o", "--output", help="Path to output annotation file", default="annotations.json")

args = parser.parse_args()



# Open the video file
video_path = args.video
output_dir= args.output

video_name = re.sub(r".*/([^/]+)\.mp4$", r"\1", video_path)

os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)

frame_number = 40
num_images = 140

while frame_number < num_images:
    ret, frame = cap.read()  # Read a frame
    if not ret:
        break  # Stop if the video ends

    image_path = os.path.join(output_dir, f"{video_name}_{frame_number}.jpg")
      # Save the frame as an image
    if cv2.imwrite(image_path, frame):
        print(f"Saved {image_path}")
    else:
        print(f"Failed to save {image_path}")

    frame_number += 1

cap.release()
cv2.destroyAllWindows()