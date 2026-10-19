# Quantum random numbers and key security

My final-year project at NIT Silchar on quantum security. It has two parts:

1. **qrngsim**, a Python package that generates random bits three ways and benchmarks them against each other.
2. **A Grover attack estimate** for ECDH keys built from those random bits, to check whether a quantum computer running Grover's search could recover them.

## Random number sources

| Method | Where the randomness comes from | Notes |
|---|---|---|
| Qiskit simulation | A simulated qubit put through a Hadamard gate and measured | Fast, but it is a simulation, so the output is only as random as the simulator |
| ANU quantum API | Vacuum fluctuations measured by the Australian National University's QRNG service | Physically random, limited by network speed |
| Classical | Python's `secrets` module, backed by the OS's cryptographic RNG | Fastest; the baseline |

For the Qiskit source, each bit is one measurement of a qubit prepared in an equal superposition:

```
|0⟩ → H → (|0⟩ + |1⟩)/√2 → measure → 0 or 1, each with probability 1/2
```

## Grover attack estimate

`qrngsim/grovers_algorithm.py` builds a P-256 ECDH private key from a QRNG source (Qiskit, random.org, or `secrets` as a fallback), derives a real shared secret, and then estimates how long a Grover-only key search would take given an oracle rate, a number of quantum processors and a time budget. It reports whether the attack fits in the budget. The point it makes: Grover's quadratic speed-up does not make a QRNG predictable, and a Grover-only search of a P-256 key space stays far outside any realistic budget.

```bash
python -m qrngsim.grovers_algorithm --qrng-source auto
python -m qrngsim.grovers_algorithm --oracle-rate 1e12 --quantum-processors 1000000 --attack-window-years 10
```

Other options: `--qrng-source {auto,qiskit,randomorg,secrets}`, `--randomorg-timeout`, `--assume-predictive-oracle`, and `--show-sensitive` to print the private scalar and shared secret (off by default).

## Installation

Python 3.9 or newer.

```bash
git clone https://github.com/arif481/Final_Year_Project.git
cd Final_Year_Project
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"     # or: pip install -r requirements.txt
```

## Using qrngsim

From the command line:

```bash
qrngsim benchmark                       # time all three sources on 1,024 bits and plot the result
qrngsim benchmark -b 2000 -o results.png
qrngsim generate -m quantum -b 256
qrngsim generate -m classical -b 128 --hex
```

From Python:

```python
from qrngsim import QuantumSimulatorRNG, run_benchmark, plot_results

rng = QuantumSimulatorRNG()
bits = rng.generate_bits(256)
value = rng.generate_int(1, 100)

plot_results(run_benchmark(target_bits=1024))
```

`notebooks/QRNG_Simulation.ipynb` walks through the same comparison with bit-distribution plots.

## Layout

```
qrngsim/
  generators/          base class plus the quantum_simulator, anu_api and classical sources
  benchmark.py         timing and comparison
  visualization.py     plots
  grovers_algorithm.py ECDH key generation and the Grover attack estimate
  cli.py               the qrngsim command
tests/                 pytest tests for the generators and benchmark
notebooks/             the walkthrough notebook
```

Run the tests with `pytest`.

## References

- [Qiskit documentation](https://docs.quantum.ibm.com/)
- [ANU Quantum Random Numbers](https://qrng.anu.edu.au/)

## License

[MIT](LICENSE)
