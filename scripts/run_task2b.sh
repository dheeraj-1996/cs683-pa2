#!/bin/bash
# runs dynamic i-rrip at L2 on all traces for 5 thresholds (no L1D prefetcher, 25M warmup + 25M sim)
# lru / srrip / i-rrip results for comparison come from run_task2a.sh
# build first:
#   ./build_champsim.sh no dyn_irrip dyn_irrip
# usage: ./scripts/run_task2b.sh <trace dir>

TRACES=${1:-../traces}
mkdir -p results/task2b

for thr in 0.05 0.15 0.25 0.35 0.45; do
    for t in $TRACES/*.champsimtrace.*; do
        name=$(basename $t | cut -d. -f1)
        DYN_THRESHOLD=$thr ./bin/*-1core-dyn_irrip -warmup_instructions 25000000 -simulation_instructions 25000000 \
            -traces $t > results/task2b/${name}_dyn_$thr.txt 2>&1 &
    done
done
wait
