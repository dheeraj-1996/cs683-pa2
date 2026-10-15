#!/bin/bash
# runs spp at L1D with the prefetch aware dynamic i-rrip at L2 on all traces (25M warmup + 25M sim)
# standalone spp comes from run_task1.sh and dynamic i-rrip from run_task2b.sh
# build first:
#   ./build_champsim.sh spp dyn_irrip spp_dyn
# usage: ./scripts/run_task3.sh <trace dir>

source "$(dirname "$0")/lib.sh"
TRACES=${1:-../traces}
check_traces $TRACES
mkdir -p results/task3
bin=$(find_bin spp_dyn) || exit 1

for t in $TRACES/*.champsimtrace.*; do
    name=$(basename $t | cut -d. -f1)
    run_sim $bin $t results/task3/${name}_spp_dyn.txt
done
wait
