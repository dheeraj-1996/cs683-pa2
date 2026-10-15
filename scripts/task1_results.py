# prints the task 1 table and makes the figures and LaTeX table from the champsim outputs
# usage: python3 scripts/task1_results.py

import plotlib as pl

DIR = "results/task1"
configs = ["baseline", "ipstride", "spp"]
names = {"baseline": "No prefetcher", "ipstride": "IP-stride", "spp": "SPP"}

stats = {t: {c: pl.read(f"{DIR}/{t}_{c}.txt") for c in configs} for t in pl.TRACES}
pl.add_relative(stats, "baseline")

rows = []
for t in pl.TRACES:
    for c in configs:
        s = stats[t][c]
        acc, cov = ("-", "-") if c == "baseline" else ("%.2f" % s["accuracy"], "%.2f" % s["coverage"])
        rows.append([t, names[c], "%.4f" % s["ipc"], "%.4f" % s["speedup"], "%.3f" % s["l1d_mpki"], acc, cov])

header = ["Trace", "Config", "IPC", "Speedup", "L1D load MPKI", "Accuracy (%)", "Coverage (%)"]
print("| " + " | ".join(header) + " |")
print("|---" * len(header) + "|")
for r in rows:
    print("| " + " | ".join(r) + " |")

pl.ieee_style()
pl.latex_table(f"{DIR}/table.tex", "L1D prefetchers: performance and prefetch quality (25M instructions)", "tab:task1",
               ["Trace", "Config", "IPC", "Speedup", "L1D MPKI", "Acc. (\\%)", "Cov. (\\%)"], rows)

pf = ["ipstride", "spp"]
pl.bars(stats, pf, names, "speedup", "Speedup over no prefetcher", f"{DIR}/speedup", order=configs)
pl.bars(stats, configs, names, "l1d_mpki", "L1D load MPKI", f"{DIR}/mpki")
pl.bars(stats, pf, names, "accuracy", "Prefetch accuracy (%)", f"{DIR}/accuracy", order=configs)
pl.bars(stats, pf, names, "coverage", "L1D miss coverage (%)", f"{DIR}/coverage", order=configs)
