# prints the task 2b table and makes the figures and LaTeX table
# lru / srrip / i-rrip come from results/task2a, dynamic i-rrip from results/task2b
# usage: python3 scripts/task2b_results.py

import plotlib as pl

DIR = "results/task2b"
thresholds = ["0.05", "0.15", "0.25", "0.35", "0.45"]
BEST = "0.15"

names = {"lru": "LRU", "rrip": "SRRIP", "irrip": "I-RRIP"}
for thr in thresholds:
    names["dyn_" + thr] = "Dyn. I-RRIP (%s)" % thr

stats = {}
for t in pl.TRACES:
    stats[t] = {}
    for c in names:
        d = "results/task2a" if c in ["lru", "rrip", "irrip"] else DIR
        stats[t][c] = pl.read(f"{d}/{t}_{c}.txt")
pl.add_relative(stats, "lru")

rows = []
for t in pl.TRACES:
    for c in names:
        s = stats[t][c]
        rows.append([t, names[c], "%.4f" % s["ipc"], "%.4f" % s["speedup"],
                     "%.3f" % s["l2_mpki"], "%.3f" % s["l2_instr_mpki"], "%.3f" % s["l2_data_mpki"]])

header = ["Trace", "Policy", "IPC", "Speedup", "L2C load MPKI", "L2 instr MPKI", "L2 data MPKI"]
print("| " + " | ".join(header) + " |")
print("|---" * len(header) + "|")
for r in rows:
    print("| " + " | ".join(r) + " |")

pl.ieee_style()
pl.latex_table(f"{DIR}/table.tex", "Dynamic I-RRIP threshold sweep against LRU, SRRIP and I-RRIP (25M instructions)", "tab:task2b",
               ["Trace", "Policy", "IPC", "Speedup", "L2C MPKI", "Instr. MPKI", "Data MPKI"], rows)

# threshold sensitivity: one line per trace across the thresholds
xs = [float(thr) for thr in thresholds]
trace_names = {t: t for t in pl.TRACES}
pl.lines(xs, {t: [stats[t]["dyn_" + thr]["speedup"] for thr in thresholds] for t in pl.TRACES},
         trace_names, "Threshold", "Speedup over LRU", f"{DIR}/sensitivity_speedup", hline=1.0)
pl.lines(xs, {t: [stats[t]["dyn_" + thr]["l2_instr_mpki"] for thr in thresholds] for t in pl.TRACES},
         trace_names, "Threshold", "L2C instruction MPKI", f"{DIR}/sensitivity_l2_instr_mpki")

compare = ["lru", "rrip", "irrip", "dyn_" + BEST]
names["dyn_" + BEST] = "Dyn. I-RRIP"
pl.bars(stats, compare[1:], names, "speedup", "Speedup over LRU", f"{DIR}/speedup", order=compare)
pl.bars(stats, compare, names, "l2_mpki", "L2C load MPKI", f"{DIR}/l2c_mpki")
pl.bars(stats, compare, names, "l2_instr_mpki", "L2C instruction MPKI", f"{DIR}/l2_instr_mpki")
pl.bars(stats, compare, names, "l2_data_mpki", "L2C data MPKI", f"{DIR}/l2_data_mpki")
