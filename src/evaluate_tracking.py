import json
from shapely.geometry import box
from collections import defaultdict
import re
import os


def iou(b1, b2):
    """Calculate IoU between two [x1, y1, x2, y2] boxes."""
    box1 = box(*b1)
    box2 = box(*b2)
    inter = box1.intersection(box2).area
    union = box1.union(box2).area
    return inter / union if union > 0 else 0

def load_gt_and_tracker(gt_path, tracker_path):
    with open(gt_path) as f:
        gt = json.load(f)
    with open(tracker_path) as f:
        tracker = json.load(f)
    return gt["frames"], tracker

def evaluate_partial_track(gt_frames, tracker_frames, start_frame, iou_thresh=0.5):
    matched_id_counts = defaultdict(int)
    total_gt_frames = len(gt_frames)

    print(f"Lenght of the track: {total_gt_frames}")

    matched_frames = 0

    for frame_str, gt_boxes in gt_frames.items():

        frame_str = str(int(frame_str) + start_frame)

        print(f"Processing frame number: {frame_str}/{total_gt_frames + start_frame - 1}")
        if not gt_boxes:
            # TODO can happen
            continue
        gt_box = gt_boxes[0]
        if frame_str not in tracker_frames:
            print(f"No detection in frame: {frame_str}")
            continue

        best_iou = 0
        best_id = None
        for track_id, det_boxes in tracker_frames[frame_str].items():
            for det_box in det_boxes:
                i = iou(gt_box, det_box)
                if i > best_iou:
                    best_iou = i
                    best_id = track_id
        if best_iou >= iou_thresh:
            matched_frames += 1
            matched_id_counts[best_id] += 1

    if matched_id_counts:
        best_tracker_id = max(matched_id_counts, key=matched_id_counts.get)
        IDTP = matched_id_counts[best_tracker_id]
        IDFN = total_gt_frames - IDTP
        IDFP = sum(matched_id_counts.values()) - IDTP
    else:
        IDTP = 0
        IDFN = total_gt_frames
        IDFP = 0

    IDPrecision = IDTP / (IDTP + IDFP) if (IDTP + IDFP) > 0 else 0
    IDRecall = IDTP / (IDTP + IDFN) if (IDTP + IDFN) > 0 else 0
    IDF1 = 2 * IDPrecision * IDRecall / (IDPrecision + IDRecall) if (IDPrecision + IDRecall) > 0 else 0

    return {
        "IDTP": IDTP,
        "IDFP": IDFP,
        "IDFN": IDFN,
        "IDPrecision": IDPrecision,
        "IDRecall": IDRecall,
        "IDF1": IDF1
    }



# Example usage:
gt_path = "ground_truth_tracks/gt_d3_01_0-150_3.json"
tracker_path = "tracking_results/d3_01.json"

print(f"Evaluating file: {os.path.basename(gt_path)}")

match = re.search(r'_(\d+)-\d+_\d+\.json$', gt_path)
if match:
    start_frame = int(match.group(1))
    print(f"Track starting at frame: {start_frame}")
else:
    print("Pattern not found")

start_frame = 0

gt_frames, tracker_frames = load_gt_and_tracker(gt_path, tracker_path)
results = evaluate_partial_track(gt_frames, tracker_frames, start_frame)
print(results)