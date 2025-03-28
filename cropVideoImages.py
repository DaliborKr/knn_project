import cv2
import argparse
import os
import re
import random


# example usage: python cropVideoImages -r 640 -d cropImgTest/3/ -n 30

def set_coordinates(frame_width, frame_height):
    x = random.randint(0, frame_width - resolution - 1)
    y = random.randint(0, frame_height - resolution - 1)

    return x, y, x + resolution, y + resolution

def get_random_frames():
    frames = []
    for _ in range(number_of_frames):
        r_frame_num = random.randint(0, 999)
        r_video_path = videos[random.randint(0, len(videos) - 1)]
        frames.append((r_video_path, r_frame_num))
    return frames

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--resolution", type=int, help="Path to input annotation file", default=640)
parser.add_argument("-d", "--directory", help="Path to output directory", default="")
parser.add_argument("-n", "--number", type=int, help="Number of frames", default=20)

args = parser.parse_args()


output_dir = args.directory if args.directory else os.getcwd()
resolution = args.resolution
number_of_frames = args.number

os.makedirs(output_dir, exist_ok=True)

videos = [
 "BuoT/Density1/d1_01.mp4",
 "BuoT/Density1/d1_02.mp4",
 "BuoT/Density2/d2_01.mp4",
 "BuoT/Density2/d2_02.mp4",
 "BuoT/Density3/d3_01.mp4",
 "BuoT/Density3/d3_02.mp4",
 "BuoT/Density4/d4_01.mp4",
 "BuoT/Density4/d4_02.mp4"
]

frames_random = get_random_frames()


for current_video, current_frame in frames_random:

    video_name = re.sub(r".*/([^/]+)\.mp4$", r"\1", current_video)


    cap = cv2.VideoCapture(current_video)
    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    ret, frame = cap.read()  # Read a frame
    if not ret:
        break  # Stop if the video ends

    x1, y1, x2, y2 = set_coordinates(frame_width, frame_height)
    cropped_frame = frame[y1:y2, x1:x2]

    image_path = os.path.join(output_dir, f"{video_name}-r{resolution}-f{current_frame}.jpg")
      # Save the frame as an image
    if cv2.imwrite(image_path, cropped_frame):
        print(f"Saved {image_path} -> video: {current_video}, frame: {current_frame} ({x1}, {y1} ; {x2}, {y2})")
    else:
        print(f"Failed to save {image_path}")

    current_frame += 1
    cap.release()

print("Done!")