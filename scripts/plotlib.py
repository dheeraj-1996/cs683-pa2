# shared code for the task*_results.py scripts: parsing the champsim output,
# IEEE style figures and LaTeX tables
#
# figures are sized for one IEEE column (3.5 in) with 8 pt Times-like text and
# saved as PDF (fonts embedded, for the report) and PNG (for a quick look).
# every bar has a black edge and a hatch so the plots still work in grayscale.

import math
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TRACES = ["trace1", "trace2", "trace3"]

COLUMN_WIDTH = 3.5      # inches, one IEEE column
HEIGHT = 1.9

# categorical colors in fixed order (checked for colorblind separation)
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
HATCHES = ["", "////", "\\\\\\\\", "...."]
MARKERS = ["o", "s", "^", "D"]


def ieee_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Nimbus Roman", "Nimbus Roman No9 L", "Times", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 7,
        "axes.linewidth": 0.6,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.axisbelow": True,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": "#cccccc",
        "grid.linewidth": 0.4,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "hatch.linewidth": 0.4,
        "legend.frameon": False,
        "pdf.fonttype": 42,     # embed TrueType fonts, IEEE PDF eXpress wants embedded fonts
        "ps.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })


def read(path):
    """pull the numbers we need out of one champsim output file"""
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


def add_relative(stats, base):
    """speedup and L1D coverage of every config against stats[t][base]"""
    for t in stats:
        b = stats[t][base]
        for s in stats[t].values():
            s["speedup"] = s["ipc"] / b["ipc"]
            s["coverage"] = 100 * (b["l1d_misses"] - s["l1d_misses"]) / b["l1d_misses"]


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def _save(fig, path):
    fig.savefig(path + ".pdf")
    fig.savefig(path + ".png", dpi=300)
    plt.close(fig)
    print("wrote", path + ".pdf")


def bars(stats, configs, names, metric, ylabel, path, order=None, height=HEIGHT, ncol=None):
    """grouped bars, one group per trace and one bar per config.
    for speedup the bars start at 1.0 and a geometric mean group is added.
    order is the full config list of the task: a config's color and hatch come
    from its place in it, so it looks the same in every figure"""
    order = order or configs
    speedup = metric == "speedup"
    groups = TRACES + (["GM"] if speedup else [])
    n = len(configs)
    width = 0.8 / n

    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH, height))
    for i, c in enumerate(configs):
        k = order.index(c)
        ys = [stats[t][c][metric] for t in TRACES]
        if speedup:
            ys.append(geomean(ys))
        xs = [j + (i - (n - 1) / 2) * width for j in range(len(groups))]
        base = 1.0 if speedup else 0.0
        ax.bar(xs, [y - base for y in ys], width, bottom=base, label=names[c],
               color=COLORS[k], hatch=HATCHES[k], edgecolor="black", linewidth=0.4)

    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.5, len(groups) - 0.5)
    ax.set_ylabel(ylabel)

    if speedup:
        v = [stats[t][c]["speedup"] for t in TRACES for c in configs] + [1.0]
        pad = 0.15 * (max(v) - min(v)) or 0.005
        ax.set_ylim(min(v) - pad, max(v) + pad)
        ax.axhline(1.0, color="black", linewidth=0.6)
        ax.axvline(len(TRACES) - 0.5, color="#888888", linewidth=0.5, linestyle=":")
    else:
        ax.set_ylim(0, ax.get_ylim()[1] * 1.05)

    # legend sits above the plot so it never covers a bar
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=ncol or n,
              handlelength=1.4, columnspacing=1.0, borderaxespad=0.2)
    _save(fig, path)


def lines(xs, series, names, xlabel, ylabel, path, height=HEIGHT, hline=None):
    """one line per key in series (dict key -> list of y values over xs)"""
    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH, height))
    for i, k in enumerate(series):
        ax.plot(xs, series[k], color=COLORS[i], marker=MARKERS[i], markersize=4,
                linewidth=1.2, label=names[k], markeredgecolor="black", markeredgewidth=0.4)
    if hline is not None:
        ax.axhline(hline, color="black", linewidth=0.6)
    ax.set_xticks(xs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=len(series),
              handlelength=1.8, borderaxespad=0.2)
    _save(fig, path)


def latex_table(path, caption, label, header, rows, group_by_first=True):
    """booktabs table for \\input{} in the report (needs booktabs and adjustbox).
    rows are lists of already formatted strings. with group_by_first a rule is
    put between traces and the trace name is only printed once"""
    cols = "l" * 2 + "r" * (len(header) - 2)
    out = ["\\begin{table}[t]", "\\centering", "\\caption{%s}" % caption, "\\label{%s}" % label,
           "\\footnotesize", "\\setlength{\\tabcolsep}{3pt}",
           "\\begin{adjustbox}{max width=\\linewidth}", "\\begin{tabular}{%s}" % cols, "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    prev = None
    for r in rows:
        r = ["--" if x == "-" else x for x in r]
        if group_by_first:
            if prev is not None and r[0] != prev:
                out.append("\\midrule")
            first = r[0]
            if r[0] == prev:
                r[0] = ""
            prev = first
        out.append(" & ".join(r) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", "\\end{table}", ""]
    open(path, "w").write("\n".join(out))
    print("wrote", path)
