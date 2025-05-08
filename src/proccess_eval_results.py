import matplotlib.pyplot as plt
import json
import numpy as np
import os
import plotly.express as px
import pandas as pd
import re
import seaborn as sns


def generate_latex_table(results_dict):
    headers = [
        "Tracker", "IDF1", "IDPrec", "IDRec",
        "IDTP", "IDFP", "IDFN",
        "Switch", "Frag", "meanIDs", "meanBestLen"
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
            f"{metrics['ID_SWITCH']}",
            f"{metrics['FRAG']}",
            f"{metrics.get('MEAN_DIFF_IDS_CNT', '-')}",
            f"{metrics.get('MEAN_BEST_TRACK_LEN', '-')}"
        ]
        latex.append(" & ".join(row) + " \\\\")

    # Footer
    latex += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\caption{Tracking performance summary (aggregated over all tracks).}",
        "\\label{tab:tracking_results}",
        "\\end{table}"
    ]

    return "\n".join(latex)




results_dir = "eval_results/eval1"

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
        print(match.group(1))

    for result in results:
        if result.get("GT_FILENAME") == "ALL":
            # final result
            result = next((entry for entry in results if entry.get("GT_FILENAME") == "ALL"), None)
            print(result)



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


# TODO select records with at least one bad IDF1 (thresh hold = 0.85?)
# TODO do the same thing for id switches

print(results_gt)


df = pd.DataFrame(results_gt).T  # GTs as rows
plt.figure(figsize=(7, 15))
sns.heatmap(df, annot=True, fmt=".2f", cmap="GnBu", annot_kws={"size": 7}, linewidths=0.5,
            linecolor='black', vmin=0.7, vmax=1.0)
plt.title("IDF1 per GT Track and Tracker")
plt.xlabel("Tracker")
plt.ylabel("GT Track")
plt.xticks(fontsize=7)
plt.yticks(fontsize=7)
plt.tight_layout()
plt.show()

latex_str = generate_latex_table(result_all)
print("\n\n")
print(latex_str)


# plt.bar(trackers, idf1)
# plt.title("IDF1 Comparison")
# plt.ylabel("IDF1 Score")
# plt.ylim(0, 1)
# plt.show()


# x = np.arange(len(trackers))
# width = 0.25

# fig, ax = plt.subplots()
# ax.bar(x - width, idf1, width, label='IDF1')
# ax.bar(x, id_switch, width, label='ID Switches')
# ax.bar(x + width, frag, width, label='Fragments')

# ax.set_ylabel('Score / Count')
# ax.set_title('Tracker Comparison')
# ax.set_xticks(x)
# ax.set_xticklabels(trackers)
# ax.legend()

# plt.show()



# df = pd.DataFrame({
#     'metric': ['IDF1', 'Precision', 'Recall', 'ID_SWITCH', 'FRAG'],
#     'Tracker A': [0.96, 0.98, 0.95, 2, 1],
#     'Tracker B': [0.91, 0.92, 0.90, 8, 4]
# })

# # Convert to long format for Plotly
# df_long = df.melt(id_vars='metric', var_name='Tracker', value_name='Score')

# # Plot with color by tracker
# fig = px.line_polar(df_long, r='Score', theta='metric', color='Tracker', line_close=True)
# fig.show()
