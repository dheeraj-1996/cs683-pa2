#!/bin/bash
# runs lru, srrip and i-rrip at L2 on all traces (no L1D prefetcher, 25M warmup + 25M sim)
# build first:
#   ./build_champsim.sh no lru lru
#   ./build_champsim.sh no rrip rrip
#   ./build_champsim.sh no irrip irrip
# usage: ./scripts/run_task2a.sh <trace dir>

TRACES=${1:-../traces}
mkdir -p results/task2a

for b in lru rrip irrip; do
    for t in $TRACES/*.champsimtrace.*; do
        name=$(basename $t | cut -d. -f1)
        ./bin/*-1core-$b -warmup_instructions 25000000 -simulation_instructions 25000000 \
            -traces $t > results/task2a/${name}_$b.txt 2>&1 &
    done
done
wait
