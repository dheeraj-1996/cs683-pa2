# prints the task 3 table and makes the plots
# no prefetcher and spp come from results/task1, dynamic i-rrip from results/task2b
# usage: python3 scripts/task3_results.py

import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "results/task3"
traces = ["trace1", "trace2", "trace3"]
files = {
    "baseline": "results/task1/{}_baseline.txt",
    "spp": "results/task1/{}_spp.txt",
    "dyn": "results/task2b/{}_dyn_0.15.txt",
    "spp_dyn": DIR + "/{}_spp_dyn.txt",
}
names = {"baseline": "No prefetcher + LRU", "spp": "SPP + LRU", "dyn": "No prefetcher + Dynamic I-RRIP", "spp_dyn": "SPP + Dynamic I-RRIP"}


def read(path):
    text = open(path).read()
    l1d = re.search(r"L1D LOAD\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+).*MPKI: ([\d.]+)", text)
    acc = re.search(r"L1D USEFUL LOAD PREFETCHES:.*ACCURACY:\s+(\S+)", text).group(1)
    return {
        "ipc": float(re.findall(r"CPU 0 cumulative IPC: ([\d.]+)", text)[-1]),
        "l1d_misses": int(l1d.group(1)),
        "l1d_mpki": float(l1d.group(2)),
        "accuracy": 0.0 if "nan" in acc else float(acc),
        "l2_mpki": float(re.search(r"L2C LOAD\s+ACCESS:.*MPKI: ([\d.]+)", text).group(1)),
        "l2_instr_mpki": float(re.search(r"L2C INSTRUCTION LOAD MPKI: ([\d.]+)", text).group(1)),
        "l2_data_mpki": float(re.search(r"L2C DATA LOAD MPKI: ([\d.]+)", text).group(1)),
    }


stats = {}
for t in traces:
    stats[t] = {c: read(f.format(t)) for c, f in files.items()}
    base = stats[t]["baseline"]
    for s in stats[t].values():
        s["speedup"] = s["ipc"] / base["ipc"]
        s["coverage"] = 100 * (base["l1d_misses"] - s["l1d_misses"]) / base["l1d_misses"]

print("| Trace | Config | IPC | Speedup | Accuracy (%) | Coverage (%) | L1D MPKI | L2C MPKI | L2 Instr MPKI | L2 Data MPKI |")
print("|---|---|---|---|---|---|---|---|---|---|")
for t in traces:
    for c in files:
        s = stats[t][c]
        if c in ["spp", "spp_dyn"]:
            acc, cov = "%.2f" % s["accuracy"], "%.2f" % s["coverage"]
        else:
            acc, cov = "-", "-"
        print("| %s | %s | %.4f | %.4f | %s | %s | %.3f | %.3f | %.3f | %.3f |" % (t, names[c], s["ipc"], s["speedup"], acc, cov,
              s["l1d_mpki"], s["l2_mpki"], s["l2_instr_mpki"], s["l2_data_mpki"]))


def plot(configs, metric, ylabel, fname):
    width = 0.8 / len(configs)
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, c in enumerate(configs):
        xs = [j + (i - (len(configs) - 1) / 2) * width for j in range(len(traces))]
        bars = ax.bar(xs, [stats[t][c][metric] for t in traces], width, label=names[c])
        ax.bar_label(bars, fmt="%.4f" if metric == "speedup" else "%.2f", fontsize=7)

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

    ax.legend(loc="upper left", ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{DIR}/{fname}", dpi=150)
    plt.close(fig)


plot(["spp", "dyn", "spp_dyn"], "speedup", "Speedup over no prefetcher + LRU", "speedup.png")
plot(["spp", "spp_dyn"], "accuracy", "Prefetch accuracy (%)", "accuracy.png")
plot(["spp", "spp_dyn"], "coverage", "L1D coverage (%)", "coverage.png")
plot(list(files), "l1d_mpki", "L1D load MPKI", "l1d_mpki.png")
plot(list(files), "l2_mpki", "L2C load MPKI", "l2c_mpki.png")
plot(list(files), "l2_instr_mpki", "L2 instruction load MPKI", "l2_instr_mpki.png")
plot(list(files), "l2_data_mpki", "L2 data load MPKI", "l2_data_mpki.png")
