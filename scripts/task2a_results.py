# prints the task 2a table and makes the figures and LaTeX table from the champsim outputs
# usage: python3 scripts/task2a_results.py

import plotlib as pl

DIR = "results/task2a"
configs = ["lru", "rrip", "irrip"]
names = {"lru": "LRU", "rrip": "SRRIP", "irrip": "I-RRIP"}

stats = {t: {c: pl.read(f"{DIR}/{t}_{c}.txt") for c in configs} for t in pl.TRACES}
pl.add_relative(stats, "lru")

rows = []
for t in pl.TRACES:
    for c in configs:
        s = stats[t][c]
        rows.append([t, names[c], "%.4f" % s["ipc"], "%.4f" % s["speedup"],
                     "%.3f" % s["l2_mpki"], "%.3f" % s["l2_instr_mpki"], "%.3f" % s["l2_data_mpki"]])

header = ["Trace", "Policy", "IPC", "Speedup", "L2C load MPKI", "L2 instr MPKI", "L2 data MPKI"]
print("| " + " | ".join(header) + " |")
print("|---" * len(header) + "|")
for r in rows:
    print("| " + " | ".join(r) + " |")

pl.ieee_style()
pl.latex_table(f"{DIR}/table.tex", "L2C replacement policies, no L1D prefetcher (25M instructions)", "tab:task2a",
               ["Trace", "Policy", "IPC", "Speedup", "L2C MPKI", "Instr. MPKI", "Data MPKI"], rows)

pl.bars(stats, ["rrip", "irrip"], names, "speedup", "Speedup over LRU", f"{DIR}/speedup", order=configs)
pl.bars(stats, configs, names, "l2_mpki", "L2C load MPKI", f"{DIR}/l2c_mpki")
pl.bars(stats, configs, names, "l2_instr_mpki", "L2C instruction MPKI", f"{DIR}/l2_instr_mpki")
pl.bars(stats, configs, names, "l2_data_mpki", "L2C data MPKI", f"{DIR}/l2_data_mpki")
