import cv2
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", help="Path to input video", required=True)
parser.add_argument("-d", "--directory", help="Output directory", default=None)
parser.add_argument("-s", "--segment", type=int, help="Number of frames in one segment.", default=50)


args = parser.parse_args()


video_path = args.video
output_dir = args.directory if args.directory else os.getcwd()
segment_size = args.segment

filename = os.path.basename(video_path)
name_only = os.path.splitext(filename)[0]


cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

frame_count = 0

os.makedirs(output_dir, exist_ok=True)

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break  # End of video
    
    # If the frame count is a multiple of `frames_per_segment`, start a new segment
    if frame_count % segment_size == 0:
        # Define output file name for the new segment
        end_segment_frame = frame_count + segment_size - 1 if frame_count + segment_size - 1 < total_frames - 1 else total_frames - 1
        segment_file = os.path.join(output_dir, f'{name_only}_{frame_count}-{end_segment_frame}.mp4')
        
        # Initialize a VideoWriter for the new segment
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change codec here
        out = cv2.VideoWriter(segment_file, fourcc, fps, (frame_width, frame_height))
    
    out.write(frame)
    frame_count += 1

cap.release()
out.release()

print("Video has been split into segments successfully.")