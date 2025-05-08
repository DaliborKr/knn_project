import json
from shapely.geometry import box
from collections import defaultdict
import re
import os
import sys

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

def calculate_prec_rec_idf1(idtp, idfp, idfn):
    idPrecision = idtp / (idtp + idfp) if (idtp + idfp) > 0 else 0
    idRecall = idtp / (idtp + idfn) if (idtp + idfn) > 0 else 0
    idf1 = 2 * idPrecision * idRecall / (idPrecision + idRecall) if (idPrecision + idRecall) > 0 else 0

    return idPrecision, idRecall, idf1

def analyze_tracking(match_info, best_tracker_id):
    match_info_sorted = sorted(match_info, key=lambda x: int(x[0]))

    fragmentations = 0
    id_switches = 0
    best_track_length = 0

    prev_id = None
    in_gap = False
    in_best_track = False


    for _, current_id in match_info_sorted:
        if current_id == -1:
            if in_best_track:
                best_track_length += 1
            in_gap = True
        else:
            if in_gap and current_id != prev_id:
                fragmentations += 1
            if prev_id is not None and current_id != prev_id:
                id_switches += 1

            if current_id == best_tracker_id:
                best_track_length += 1
                in_best_track = True
            else:
                in_best_track = False

            prev_id = current_id
            in_gap = False

    return fragmentations, id_switches, best_track_length


def evaluate_partial_track(gt_frames, tracker_frames, start_frame, iou_thresh=0.5):
    matched_id_counts = defaultdict(int)
    total_gt_frames = len(gt_frames)

    print(f"Lenght of the track: {total_gt_frames}")

    matched_frames = 0

    match_info = []  # Stores (frame, best_iou, best_id)

    for frame_str, gt_boxes in gt_frames.items():

        frame_str_adj = str(int(frame_str) + start_frame)

        #print(f"Processing frame number: {frame_str_adj}/{total_gt_frames + start_frame - 1}")
        if not gt_boxes:
            continue
        gt_box = gt_boxes[0]
        if frame_str_adj not in tracker_frames:
            continue

        best_iou = 0
        best_id = None

        for track_id, det_boxes in tracker_frames[frame_str_adj].items():
            for det_box in det_boxes:
                i = iou(gt_box, det_box)
                if i > best_iou:
                    best_iou = i
                    best_id = track_id
        if best_iou >= iou_thresh:
            matched_frames += 1
            matched_id_counts[best_id] += 1
        else:
            best_id = -1

        match_info.append((frame_str_adj, best_id))

    # Determine best tracker ID
    best_tracker_id = max(matched_id_counts, key=matched_id_counts.get) if matched_id_counts else None
    different_ids_cnt = len(matched_id_counts)

    # Now evaluate IDTP, IDFP, IDFN from match_info
    idtp = 0
    idfp = 0
    idfn = 0

    for frame_str_adj, best_id in match_info:
        if best_id != -1:
            if best_id == best_tracker_id:
                idtp += 1
            else:
                idfp += 1
        else:
            idfn += 1

    idPrecision, idRecall, idf1 = calculate_prec_rec_idf1(idtp, idfp, idfn)

    fragmentations, id_switches, best_track_length = analyze_tracking(match_info, best_tracker_id)

    return {
        "IDTP": idtp,
        "IDFP": idfp,
        "IDFN": idfn,
        "IDPrecision": idPrecision,
        "IDRecall": idRecall,
        "IDF1": idf1,
        "FRAG": fragmentations,
        "ID_SWITCH": id_switches,
        "DIFF_IDS_CNT": different_ids_cnt,
        "BEST_TRACK_LEN": best_track_length
    }


# INPUT:
gt_dir = "ground_truth_tracks"
trackers_output_dir = "tracking_results_botsort"


results_file_path = "eval_results/eval1/eval_botsort.json"



gt_filenames = os.listdir(gt_dir)

max_eval = 10000
eval_cnt = 0

results_all = []

idtp = 0
idfp = 0
idfn = 0
fragmentations = 0
id_switches = 0
different_ids_cnts = []
best_track_lengths = []



for gt_filename in gt_filenames:
    gt_path = os.path.join(gt_dir, gt_filename)


    match = re.search(r'_(d\d_\d\d)_(\d+)-\d+_\d+\.json$', gt_path)


    if match:
        tracker_path = os.path.join(trackers_output_dir, (match.group(1) + ".json"))

        if not os.path.isfile(tracker_path):
            print(f"No tracker data. File '{match.group(1) + ".json"}' not found in directory '{trackers_output_dir}/'.")
            continue


        print(f"Ground truth file: {os.path.basename(gt_path)}, Tracker output file: {tracker_path}")


        start_frame = int(match.group(2))
        print(f"Track starting at frame: {start_frame}")

        gt_frames, tracker_frames = load_gt_and_tracker(gt_path, tracker_path)
        results = evaluate_partial_track(gt_frames, tracker_frames, start_frame)
        print(f"{os.path.basename(gt_path)} results: {results}\n")

        results["GT_FILENAME"] = os.path.basename(gt_path)
        results_all.append(results)


        idtp += results["IDTP"]
        idfp += results["IDFP"]
        idfn += results["IDFN"]
        fragmentations += results["FRAG"]
        id_switches += results["ID_SWITCH"]
        different_ids_cnts.append(results["DIFF_IDS_CNT"])
        best_track_lengths.append(results["BEST_TRACK_LEN"])

        eval_cnt += 1


    else:
        print(f"Pattern not found in '{gt_path}'")



    if eval_cnt >= max_eval:
        break

    sys.stdout.flush()


idPrecision, idRecall, idf1 = calculate_prec_rec_idf1(idtp, idfp, idfn)
mean_different_ids_cnt = sum(different_ids_cnts) / len(different_ids_cnts)
mean_best_track_length = sum(best_track_lengths) / len(best_track_lengths)

final_results = {"IDTP": idtp,
        "IDFP": idfp,
        "IDFN": idfn,
        "IDPrecision": idPrecision,
        "IDRecall": idRecall,
        "IDF1": idf1,
        "FRAG": fragmentations,
        "ID_SWITCH": id_switches,
        "MEAN_DIFF_IDS_CNT": mean_different_ids_cnt,
        "MEAN_BEST_TRACK_LEN": mean_best_track_length,
        "GT_FILENAME": "ALL"
    }

results_all.append(final_results)
print(final_results)

with open(results_file_path, "w") as f:
                json.dump(results_all, f, indent=4)