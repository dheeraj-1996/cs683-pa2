#!/bin/bash
# runs dynamic i-rrip at L2 on all traces for 5 thresholds (no L1D prefetcher, 25M warmup + 25M sim)
# lru / srrip / i-rrip results for comparison come from run_task2a.sh
# build first:
#   ./build_champsim.sh no dyn_irrip dyn_irrip
# usage: ./scripts/run_task2b.sh <trace dir>

source "$(dirname "$0")/lib.sh"
TRACES=${1:-../traces}
check_traces $TRACES
mkdir -p results/task2b
bin=$(find_bin dyn_irrip) || exit 1

for thr in 0.05 0.15 0.25 0.35 0.45; do
    export DYN_THRESHOLD=$thr
    for t in $TRACES/*.champsimtrace.*; do
        name=$(basename $t | cut -d. -f1)
        run_sim $bin $t results/task2b/${name}_dyn_$thr.txt
    done
done
wait
