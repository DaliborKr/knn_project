import os
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", help="Path to a dataset", default="dataset6/train/")

args = parser.parse_args()
save_fig = True
fig_path = "figures/labelsPerFrame.png"


folder_path = args.dataset
set_paths = ["train/", "val/"]


data = []

for set_path in set_paths:
    folder_set_path = folder_path + set_path
    print(folder_set_path)
    for filename in os.listdir(folder_set_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_set_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                num_lines = sum(1 for _ in file)
            data.append({"filename": filename, "num_lines": num_lines})

df = pd.DataFrame(data)

total_lines = df["num_lines"].sum()
mean_lines = df["num_lines"].mean()
max_lines = df["num_lines"].max()
min_lines = df["num_lines"].min()

print("Number of labels: ", total_lines, sep="")
print("Mean number of labels per frame: ", mean_lines, sep="")
print("Min number of labels in frame: ", min_lines, sep="")
print("Max number of labels in frame: ", max_lines, sep="")


plt.figure(figsize=(10, 6))
plt.hist(df["num_lines"], bins=14, edgecolor="black")

plt.xlabel("Počet anotovaných brouků")
plt.ylabel("Počet snímků")

plt.grid(axis="y", linestyle="-", linewidth=0.3)
plt.gca().set_axisbelow(True)

x_ticks = np.arange(50, 350, 20)
plt.xticks(x_ticks)
y_ticks = np.arange(0, 11, 1)
plt.yticks(y_ticks)

# Save the plot as an image (optional)
plt.savefig(fig_path)

# Show the plot
plt.show()