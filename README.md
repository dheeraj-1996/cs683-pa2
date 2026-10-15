# ChampSim

ChampSim is a trace-based simulator for microarchitecture research.

Useful trace links:
- Traces (access requires an LDAP ID): https://drive.google.com/drive/folders/1zYchkn-M1auZp_l5wRkIzAcDYPkNtW3H?usp=sharing
- ChampSim wiki: https://champsim.github.io/ChampSim/master/index.html

## Clone the repository

```bash
git clone https://github.com/cs683-iitb-autumn-2026/pa2.git
```

## Compile

To compile ChampSim, specify three parameters: the L1D prefetcher, the L2C replacement policy, and the binary name.

For example, `./build_champsim.sh no lru baseline` builds a single-core processor with a hashed perceptron branch predictor, no L1D data prefetcher, and the LRU replacement policy for the L2C.

You can give the binary any name. Custom names help distinguish binaries that use the same configuration.

```bash
./build_champsim.sh ${L1D_PREFETCHER} ${L2C_REPLACEMENT} ${BINARY_NAME}

./build_champsim.sh no lru baseline
```

## Run simulation

```bash
./bin/[BINARY] -warmup_instructions [N_WARM] -simulation_instructions [N_SIM] -traces [TRACE_DIR]/[TRACE]
./bin/hashed_perceptron-no-no-no-no-no-no-no-lru-lru-lru-lru-lru-lru-lru-lru-1core-baseline -warmup_instructions 25000000 -simulation_instructions 25000000 -traces ../traces/trace1.champsimtrace.xz
```

Where:
- `${BINARY}`: ChampSim binary compiled by `build_champsim.sh` (for example, `hashed_perceptron-no-no-no-no-no-no-no-lru-lru-lru-lru-lru-lru-lru-lru-1core-baseline`)
- `${N_WARM}`: number of instructions for the warmup period (25 million)
- `${N_SIM}`: number of instructions for the detailed simulation (25 million)
- `${TRACE_DIR}`: directory containing the trace (for example, `../traces/`)
- `${TRACE}`: name of the trace (for example, `trace1.champsimtrace.xz`)

## Evaluate the simulation

ChampSim measures IPC (instructions per cycle) as its main performance metric. It also prints other useful metrics at the end of each simulation.

## PA2: reproducing the results

What each task adds:

| Task | Files | What it is |
|---|---|---|
| 1 | `prefetcher/spp.l1d_pref` | Stride pattern prefetcher at L1D (uniform + signature-based strides, accuracy throttling) |
| 2a | `replacement/rrip.l2c_repl`, `replacement/irrip.l2c_repl` | SRRIP and instruction-conscious I-RRIP at L2C |
| 2b | `replacement/dyn_irrip.l2c_repl` | Dynamic I-RRIP: leader sets sample the instruction share of L2 traffic, followers switch policy on a threshold (`DYN_THRESHOLD`, default 0.15) |
| 3 | `replacement/dyn_irrip.l2c_repl` | Same policy, prefetch-aware: prefetches are inserted at max RRPV and do not train the leaders |

Build the binaries the run scripts expect:

```bash
./build_champsim.sh no lru baseline
./build_champsim.sh ip_stride lru ipstride
./build_champsim.sh spp lru spp
./build_champsim.sh no lru lru
./build_champsim.sh no rrip rrip
./build_champsim.sh no irrip irrip
./build_champsim.sh no dyn_irrip dyn_irrip
./build_champsim.sh spp dyn_irrip spp_dyn
```

Run the simulations (traces default to `../traces`). Each script runs at most `JOBS` simulations at once (default: number of cores). `WARMUP` and `SIM` override the 25M instruction counts for quick tests:

```bash
./scripts/run_task1.sh ../traces
./scripts/run_task2a.sh ../traces
./scripts/run_task2b.sh ../traces
./scripts/run_task3.sh ../traces
```

Make the tables and figures. Each script prints a Markdown table and writes `results/<task>/table.tex` (booktabs) plus every figure as PDF (for LaTeX, fonts embedded) and PNG. Figures are one IEEE column wide (3.5 in) with 8 pt Times text:

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/task1_results.py
.venv/bin/python scripts/task2a_results.py
.venv/bin/python scripts/task2b_results.py
.venv/bin/python scripts/task3_results.py
```

The code builds with current GCC (tested with GCC 15.2), so the GCC 7 setup below is optional.

## Install GCC 7 on Ubuntu

```bash
sudo apt update
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
vim /etc/apt/sources.list
```

Update the last line with:

```bash
deb [arch=amd64] http://archive.ubuntu.com/ubuntu focal main universe
```

Then run:

```bash
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get install gcc-7
sudo apt-get install g++-7
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 0
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 0
```

If GCC and G++ are already present in `/usr/bin`, configure the alternatives using:

```bash
sudo update-alternatives --config g++
sudo update-alternatives --config gcc
```

