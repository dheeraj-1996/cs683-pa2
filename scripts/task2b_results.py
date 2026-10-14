# prints the task 2b table and makes the plots
# lru / srrip / i-rrip come from results/task2, dynamic i-rrip from results/task2b
# usage: python3 scripts/task2b_results.py

import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "results/task2b"
traces = ["trace1", "trace2", "trace3"]
thresholds = ["0.05", "0.15", "0.25", "0.35", "0.45"]
BEST = "0.15"

names = {"lru": "LRU", "rrip": "SRRIP", "irrip": "I-RRIP"}
for thr in thresholds:
    names["dyn_" + thr] = "Dyn " + thr


def read(path):
    text = open(path).read()
    return {
        "ipc": float(re.findall(r"CPU 0 cumulative IPC: ([\d.]+)", text)[-1]),
        "l2_instr_mpki": float(re.search(r"L2C INSTRUCTION LOAD MPKI: ([\d.]+)", text).group(1)),
        "l2_data_mpki": float(re.search(r"L2C DATA LOAD MPKI: ([\d.]+)", text).group(1)),
    }


stats = {}
for t in traces:
    stats[t] = {}
    for c in names:
        d = "results/task2" if c in ["lru", "rrip", "irrip"] else DIR
        stats[t][c] = read(f"{d}/{t}_{c}.txt")
        stats[t][c]["speedup"] = stats[t][c]["ipc"] / stats[t]["lru"]["ipc"]

print("| Trace | Policy | IPC | Speedup | L2 Instr MPKI | L2 Data MPKI |")
print("|---|---|---|---|---|---|")
for t in traces:
    for c in names:
        s = stats[t][c]
        print("| %s | %s | %.4f | %.4f | %.3f | %.3f |" % (t, names[c], s["ipc"], s["speedup"], s["l2_instr_mpki"], s["l2_data_mpki"]))


def plot(configs, metric, ylabel, fname):
    width = 0.8 / len(configs)
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, c in enumerate(configs):
        xs = [j + (i - (len(configs) - 1) / 2) * width for j in range(len(traces))]
        bars = ax.bar(xs, [stats[t][c][metric] for t in traces], width, label=names[c])
        ax.bar_label(bars, fmt="%.3f" if metric == "speedup" else "%.2f", fontsize=7)

    ax.set_xticks(range(len(traces)))
    ax.set_xticklabels(traces)
    ax.set_ylabel(ylabel)

    if metric == "speedup":
        # speedups are close to 1 so zoom in
        v = [stats[t][c]["speedup"] for t in traces for c in configs]
        ax.set_ylim(min(v) - 0.01, max(v) + 0.01)
        ax.axhline(1.0, color="gray", linestyle="--")
    else:
        ax.set_ylim(0, ax.get_ylim()[1] * 1.15)

    ax.legend(loc="upper left", ncol=len(configs), fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{DIR}/{fname}", dpi=150)
    plt.close(fig)


dyn = ["dyn_" + thr for thr in thresholds]
plot(dyn, "speedup", "Speedup over LRU", "sensitivity_speedup.png")
plot(dyn, "l2_instr_mpki", "L2 instruction load MPKI", "sensitivity_l2_instr_mpki.png")

compare = ["lru", "rrip", "irrip", "dyn_" + BEST]
plot(compare, "speedup", "Speedup over LRU", "speedup.png")
plot(compare, "l2_instr_mpki", "L2 instruction load MPKI", "l2_instr_mpki.png")
plot(compare, "l2_data_mpki", "L2 data load MPKI", "l2_data_mpki.png")
