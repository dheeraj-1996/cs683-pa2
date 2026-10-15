#!/bin/bash
# runs no prefetcher, ip_stride and spp on all traces (25M warmup + 25M sim)
# build first:
#   ./build_champsim.sh no lru baseline
#   ./build_champsim.sh ip_stride lru ipstride
#   ./build_champsim.sh spp lru spp
# usage: ./scripts/run_task1.sh <trace dir>

source "$(dirname "$0")/lib.sh"
TRACES=${1:-../traces}
check_traces $TRACES
mkdir -p results/task1

for b in baseline ipstride spp; do
    bin=$(find_bin $b) || exit 1
    for t in $TRACES/*.champsimtrace.*; do
        name=$(basename $t | cut -d. -f1)
        run_sim $bin $t results/task1/${name}_$b.txt
    done
done
wait
