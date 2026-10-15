# prints the task 3 table and makes the figures and LaTeX table
# no prefetcher and spp come from results/task1, dynamic i-rrip from results/task2b
# usage: python3 scripts/task3_results.py

import plotlib as pl

DIR = "results/task3"
DYN_THRESHOLD = "0.15"
files = {
    "baseline": "results/task1/{}_baseline.txt",
    "spp": "results/task1/{}_spp.txt",
    "dyn": "results/task2b/{}_dyn_" + DYN_THRESHOLD + ".txt",
    "spp_dyn": DIR + "/{}_spp_dyn.txt",
}
names = {"baseline": "No PF + LRU", "spp": "SPP + LRU", "dyn": "No PF + Dyn. I-RRIP", "spp_dyn": "SPP + Dyn. I-RRIP"}

stats = {t: {c: pl.read(f.format(t)) for c, f in files.items()} for t in pl.TRACES}
pl.add_relative(stats, "baseline")

rows = []
for t in pl.TRACES:
    for c in files:
        s = stats[t][c]
        acc, cov = ("%.2f" % s["accuracy"], "%.2f" % s["coverage"]) if c in ["spp", "spp_dyn"] else ("-", "-")
        rows.append([t, names[c], "%.4f" % s["ipc"], "%.4f" % s["speedup"], acc, cov,
                     "%.3f" % s["l1d_mpki"], "%.3f" % s["l2_mpki"], "%.3f" % s["l2_instr_mpki"], "%.3f" % s["l2_data_mpki"]])

header = ["Trace", "Config", "IPC", "Speedup", "Accuracy (%)", "Coverage (%)", "L1D MPKI", "L2C MPKI", "L2 instr MPKI", "L2 data MPKI"]
print("| " + " | ".join(header) + " |")
print("|---" * len(header) + "|")
for r in rows:
    print("| " + " | ".join(r) + " |")

pl.ieee_style()
# 10 columns is too wide for one column, so this one is a table* spanning both
pl.latex_table(f"{DIR}/table.tex", "SPP combined with prefetch-aware dynamic I-RRIP (25M instructions)", "tab:task3",
               ["Trace", "Config", "IPC", "Speedup", "Acc. (\\%)", "Cov. (\\%)", "L1D", "L2C", "L2 instr.", "L2 data"], rows)
tex = open(f"{DIR}/table.tex").read().replace("{table}", "{table*}")
open(f"{DIR}/table.tex", "w").write(tex)

four = list(files)
pl.bars(stats, ["spp", "dyn", "spp_dyn"], names, "speedup", "Speedup over no PF + LRU", f"{DIR}/speedup", order=four, ncol=2, height=2.1)
pl.bars(stats, ["spp", "spp_dyn"], names, "accuracy", "Prefetch accuracy (%)", f"{DIR}/accuracy", order=four)
pl.bars(stats, ["spp", "spp_dyn"], names, "coverage", "L1D miss coverage (%)", f"{DIR}/coverage", order=four)
pl.bars(stats, four, names, "l1d_mpki", "L1D load MPKI", f"{DIR}/l1d_mpki", ncol=2, height=2.1)
pl.bars(stats, four, names, "l2_mpki", "L2C load MPKI", f"{DIR}/l2c_mpki", ncol=2, height=2.1)
pl.bars(stats, four, names, "l2_instr_mpki", "L2C instruction MPKI", f"{DIR}/l2_instr_mpki", ncol=2, height=2.1)
pl.bars(stats, four, names, "l2_data_mpki", "L2C data MPKI", f"{DIR}/l2_data_mpki", ncol=2, height=2.1)
