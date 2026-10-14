# prints the task 1 table and makes the plots from the champsim outputs
# usage: python3 scripts/task1_results.py

import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "results/task1"
traces = ["trace1", "trace2", "trace3"]
configs = ["baseline", "ipstride", "spp"]
names = {"baseline": "No prefetcher", "ipstride": "IP-stride", "spp": "SPP"}


def read(path):
    text = open(path).read()
    ipc = float(re.findall(r"CPU 0 cumulative IPC: ([\d.]+)", text)[-1])
    load = re.search(r"L1D LOAD\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+).*MPKI: ([\d.]+)", text)
    acc = re.search(r"L1D USEFUL LOAD PREFETCHES:.*ACCURACY:\s+(\S+)", text).group(1)
    return {
        "ipc": ipc,
        "misses": int(load.group(1)),
        "mpki": float(load.group(2)),
        "accuracy": 0.0 if "nan" in acc else float(acc),
    }


stats = {}
for t in traces:
    stats[t] = {}
    for c in configs:
        stats[t][c] = read(f"{DIR}/{t}_{c}.txt")

    base = stats[t]["baseline"]
    for c in configs:
        s = stats[t][c]
        s["speedup"] = s["ipc"] / base["ipc"]
        s["coverage"] = 100 * (base["misses"] - s["misses"]) / base["misses"]

print("| Trace | Config | IPC | Speedup | L1D Load MPKI | Accuracy (%) | Coverage (%) |")
print("|---|---|---|---|---|---|---|")
for t in traces:
    for c in configs:
        s = stats[t][c]
        if c == "baseline":
            acc, cov = "-", "-"
        else:
            acc, cov = "%.2f" % s["accuracy"], "%.2f" % s["coverage"]
        print("| %s | %s | %.4f | %.4f | %.3f | %s | %s |" % (t, names[c], s["ipc"], s["speedup"], s["mpki"], acc, cov))


def plot(configs, metric, ylabel, fname):
    width = 0.8 / len(configs)
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, c in enumerate(configs):
        xs = [j + (i - (len(configs) - 1) / 2) * width for j in range(len(traces))]
        ys = [stats[t][c][metric] for t in traces]
        bars = ax.bar(xs, ys, width, label=names[c])
        ax.bar_label(bars, fmt="%.3f" if metric == "speedup" else "%.2f", fontsize=8)

    ax.set_xticks(range(len(traces)))
    ax.set_xticklabels(traces)
    ax.set_ylabel(ylabel)

    if metric == "speedup":
        # all speedups are close to 1 so zoom in
        ax.set_ylim(0.99, max(stats[t][c]["speedup"] for t in traces for c in configs) + 0.005)
        ax.axhline(1.0, color="gray", linestyle="--")
    else:
        ax.set_ylim(0, ax.get_ylim()[1] * 1.15)

    ax.legend(loc="upper left", ncol=len(configs))
    fig.tight_layout()
    fig.savefig(f"{DIR}/{fname}", dpi=150)
    plt.close(fig)


plot(["ipstride", "spp"], "speedup", "Speedup", "speedup.png")
plot(configs, "mpki", "L1D load MPKI", "mpki.png")
plot(["ipstride", "spp"], "accuracy", "Prefetch accuracy (%)", "accuracy.png")
plot(["ipstride", "spp"], "coverage", "L1D coverage (%)", "coverage.png")
