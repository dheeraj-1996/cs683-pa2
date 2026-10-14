#!/bin/bash
# runs spp at L1D with the prefetch aware dynamic i-rrip at L2 on all traces (25M warmup + 25M sim)
# standalone spp comes from run_task1.sh and dynamic i-rrip from run_task2b.sh
# build first:
#   ./build_champsim.sh spp dyn_irrip spp_dyn
# usage: ./scripts/run_task3.sh <trace dir>

TRACES=${1:-../traces}
mkdir -p results/task3

for t in $TRACES/*.champsimtrace.*; do
    name=$(basename $t | cut -d. -f1)
    ./bin/*-1core-spp_dyn -warmup_instructions 25000000 -simulation_instructions 25000000 \
        -traces $t > results/task3/${name}_spp_dyn.txt 2>&1 &
done
wait
