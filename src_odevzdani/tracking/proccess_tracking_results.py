import matplotlib.pyplot as plt
import json
import numpy as np
import os
import plotly.express as px
import pandas as pd
import re
import seaborn as sns


RESULTS_DIR = "tracking_eval_results"
IDF1_HEATMAP_OUT_PATH = "plots/idf1_heatmap.png"


def generate_latex_table(results_dict):
    headers = [
        "Tracker", "IDF1", "IDPrec", "IDRec",
        "IDTP", "IDFP", "IDFN",
        "Frag", "IDSwitch", "FSRatio", "meanLen"
    ]

    # Header
    latex = [
        "\\begin{table}[ht]",
        "\\centering",
        "\\begin{tabular}{lcccccccccc}",
        "\\toprule",
        " & ".join(f"\\textbf{{{h}}}" for h in headers) + " \\\\",
        "\\midrule"
    ]

    # Rows
    for tracker_name, metrics in results_dict.items():
        row = [
            tracker_name,
            f"{metrics['IDF1']:.4f}",
            f"{metrics['IDPrecision']:.4f}",
            f"{metrics['IDRecall']:.4f}",
            f"{metrics['IDTP']}",
            f"{metrics['IDFP']}",
            f"{metrics['IDFN']}",
            f"{metrics['FRAG']}",
            f"{metrics['ID_SWITCH']}",
            f"{metrics['FSRatio']:.2f}",
            f"{metrics.get('MEAN_BEST_TRACK_LEN', '-'):.2f}"
        ]
        latex.append(" & ".join(row) + " \\\\")

    # Footer
    latex += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\caption{Souhrn výsledků výkonu jednotlivých tracking algoritmů (agregováno přes všechny stopy).}",
        "\\label{tab:tracking_results}",
        "\\end{table}"
    ]

    return "\n".join(latex)




results_dir = RESULTS_DIR

trackers = []
id_prec = []
id_recall = []
idf1 = []
id_switch = []
frag = []

result_all = {}
results_gt = {}


results_filenames = os.listdir(results_dir)
for results_filename in results_filenames:
    results_path = os.path.join(results_dir, results_filename)

    with open(results_path, 'r') as f:
        results = json.load(f)

        match = re.search(r'^.+/eval_(.+).json$', results_path)
        print(f"'{match.group(1)}' results detected.")

    for result in results:
        result["FSRatio"] = result["FRAG"] / result["ID_SWITCH"] if result["ID_SWITCH"] != 0 else 0

        if result.get("GT_FILENAME") == "ALL":
            # final result
            result = next((entry for entry in results if entry.get("GT_FILENAME") == "ALL"), None)

            trackers.append(match.group(1))
            id_prec.append(result["IDPrecision"])
            id_recall.append(result["IDRecall"])
            idf1.append(result["IDF1"])
            id_switch.append(result["ID_SWITCH"])
            frag.append(result["FRAG"])

            result_all[match.group(1)] = result

        else:
            # single GT result


            results_gt.setdefault(result["GT_FILENAME"], {})[match.group(1)] = result["IDF1"]



threshold = 0.8
df = pd.DataFrame(results_gt).T  # GTs as rows
filtered_df = df[df.lt(threshold).any(axis=1)]




plt.figure(figsize=(5.2, 5))
sns.heatmap(filtered_df, annot=True, fmt=".2f", cmap="Oranges", annot_kws={"size": 8}, linewidths=0.0,
            linecolor='black', vmin=0.3, vmax=1.0)
plt.title("IDF1 per Ground Truth Track and Tracker")
plt.xlabel("Tracker")
plt.ylabel("Ground Truth Track File")
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.savefig(IDF1_HEATMAP_OUT_PATH, dpi=300)  # Save heatmap
#plt.show()

latex_str = generate_latex_table(result_all)
print("\nLatex table format:\n")
print(latex_str)
