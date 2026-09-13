"""Exploratory visualisation of Stage 3 behavioural analysis.
Compares Isolation Forest anomaly scores vs KMeans clusters on the same axes.
Not part of the pipeline — a one-off inspection tool.
"""

import matplotlib.pyplot as plt
import numpy as np

import classify


def main():
    domains, features = classify.extract_features()
    if len(domains) < 3:
        print("Not enough domains to visualise.")
        return

    anomaly = classify.run_isolation_forest(features)
    clusters = classify.run_clustering(features)

    count = features[:, 0]
    span = features[:, 1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: coloured by anomaly score
    sc1 = ax1.scatter(span, count, c=anomaly, cmap="Reds",
                      s=80, edgecolor="black", linewidth=0.5)
    ax1.set_title("Isolation Forest — anomaly score")
    ax1.set_xlabel("span (seconds active)")
    ax1.set_ylabel("contact count")
    fig.colorbar(sc1, ax=ax1, label="anomaly (higher = more unusual)")

    # Plot 2: coloured by cluster
    sc2 = ax2.scatter(span, count, c=clusters, cmap="viridis",
                      s=80, edgecolor="black", linewidth=0.5)
    ax2.set_title("KMeans — behavioural cluster")
    ax2.set_xlabel("span (seconds active)")
    ax2.set_ylabel("contact count")
    fig.colorbar(sc2, ax=ax2, label="cluster id")

    # annotate the standout domain so the demo point is obvious
    top = np.argmax(count)
    for ax in (ax1, ax2):
        ax.annotate(domains[top], (span[top], count[top]),
                    textcoords="offset points", xytext=(-10, 10),
                    fontsize=8, ha="right")

    plt.tight_layout()
    plt.savefig("data/stage3_visualisation.png", dpi=120)
    print("Saved data/stage3_visualisation.png")
    plt.show()