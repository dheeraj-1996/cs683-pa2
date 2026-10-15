#!/bin/bash
# runs lru, srrip and i-rrip at L2 on all traces (no L1D prefetcher, 25M warmup + 25M sim)
# build first:
#   ./build_champsim.sh no lru lru
#   ./build_champsim.sh no rrip rrip
#   ./build_champsim.sh no irrip irrip
# usage: ./scripts/run_task2a.sh <trace dir>

source "$(dirname "$0")/lib.sh"
TRACES=${1:-../traces}
check_traces $TRACES
mkdir -p results/task2a

for b in lru rrip irrip; do
    bin=$(find_bin $b) || exit 1
    for t in $TRACES/*.champsimtrace.*; do
        name=$(basename $t | cut -d. -f1)
        run_sim $bin $t results/task2a/${name}_$b.txt
    done
done
wait
