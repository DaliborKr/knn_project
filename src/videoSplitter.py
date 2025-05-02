import cv2
import os
import argparse


# Example usage: python src/videoSplitter.py -v BuoT/Density2/d2_01.mp4  -d splitted/test1/ -s 40 -int 4 6


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", help="Path to input video", required=True)
parser.add_argument("-d", "--directory", help="Output directory", default=None)
parser.add_argument("-s", "--segment", type=int, help="Number of frames in one segment.", default=50)
parser.add_argument("-int", "--interval", nargs=2, type=int, metavar=("START", "END"), help="Interval of chosen segment.", default=[1, 3])


args = parser.parse_args()


video_path = args.video
output_dir = args.directory if args.directory else os.getcwd()
segment_size = args.segment
first_segment = args.interval[0]
last_segment = args.interval[1]

filename = os.path.basename(video_path)
name_only = os.path.splitext(filename)[0]


cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

frame_count = 0
segment_number = 1

os.makedirs(output_dir, exist_ok=True)

out = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # End of video

    if frame_count % segment_size == 0:
        if out:
            out.release()  # Release previous segment

        if segment_number >= first_segment and segment_number <= last_segment:
            end_segment_frame = min(frame_count + segment_size - 1, total_frames - 1)
            segment_file = os.path.join(output_dir, f'{name_only}_{frame_count}-{end_segment_frame}.mp4')

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(segment_file, fourcc, fps, (frame_width, frame_height))
        else:
            out = None  # Skip writing this segment

        segment_number += 1

    if out:
        out.write(frame)

    frame_count += 1

cap.release()
if out:
    out.release()


print("Video has been split into segments successfully.")