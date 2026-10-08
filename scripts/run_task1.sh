#!/bin/bash
# runs no prefetcher, ip_stride and spp on all traces (25M warmup + 25M sim)
# build first:
#   ./build_champsim.sh no lru baseline
#   ./build_champsim.sh ip_stride lru ipstride
#   ./build_champsim.sh spp lru spp
# usage: ./scripts/run_task1.sh <trace dir>

TRACES=${1:-../traces}
mkdir -p results/task1

for b in baseline ipstride spp; do
    for t in $TRACES/*.champsimtrace.*; do
        name=$(basename $t | cut -d. -f1)
        ./bin/*-1core-$b -warmup_instructions 25000000 -simulation_instructions 25000000 \
            -traces $t > results/task1/${name}_$b.txt 2>&1 &
    done
done
wait
