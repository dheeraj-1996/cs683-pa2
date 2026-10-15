#!/bin/bash
# shared helpers for the run_task*.sh scripts, source this file
#   JOBS=<n>          max simulations at once (default: number of cores)
#   WARMUP=<n> SIM=<n> instruction counts (default 25M each), handy for quick tests

WARMUP=${WARMUP:-25000000}
SIM=${SIM:-25000000}
JOBS=${JOBS:-$(nproc)}

# check_traces <trace dir>
check_traces() {
    if ! ls "$1"/*.champsimtrace.* >/dev/null 2>&1; then
        echo "no *.champsimtrace.* files in $1" >&2
        exit 1
    fi
}

# find_bin <binary name suffix>, prints the path to bin/*-1core-<suffix>
find_bin() {
    local b=(bin/*-1core-$1)
    if [ ! -x "${b[0]}" ]; then
        echo "bin/*-1core-$1 not found, build it with ./build_champsim.sh first" >&2
        exit 1
    fi
    echo "${b[0]}"
}

# run_sim <binary> <trace> <output file>, runs in the background but never
# more than $JOBS at once
run_sim() {
    while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do
        wait -n
    done
    echo "running $(basename "$2") -> $3"
    "$1" -warmup_instructions $WARMUP -simulation_instructions $SIM -traces "$2" > "$3" 2>&1 &
}
