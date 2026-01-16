# QRNG Simulation

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for simulating and comparing **Quantum Random Number Generation (QRNG)** methods against classical approaches.

## 🎯 Overview

This project compares three different approaches to random number generation:

| Method | Source | Speed | True Randomness |
|--------|--------|-------|-----------------|
| **Local Qiskit Simulation** | Simulated quantum measurements | Fast | Simulated |
| **ANU Quantum API** | Real quantum vacuum fluctuations | Network-dependent | ✅ True |
| **Classical (Python secrets)** | OS cryptographic RNG | Very Fast | Pseudo-random |

## 🚀 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/qrngsim.git
cd qrngsim

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Dependencies Only

```bash
pip install -r requirements.txt
```

## 📖 Usage

### As a Python Library

```python
from qrngsim import QuantumSimulatorRNG, ClassicalRNG, AnuWebQRNG
from qrngsim import run_benchmark, plot_results

# Generate random bits using quantum simulation
quantum_rng = QuantumSimulatorRNG()
random_bits = quantum_rng.generate_bits(256)
print(f"Quantum bits: {random_bits[:32]}...")

# Generate random bytes
random_bytes = quantum_rng.generate_bytes(16)

# Generate random integer in range
random_int = quantum_rng.generate_int(1, 100)

# Run benchmark comparison
results = run_benchmark(target_bits=1024)
plot_results(results)
```

### Command Line Interface

```bash
# Run benchmark with default settings
qrngsim benchmark

# Benchmark with custom number of bits
qrngsim benchmark -b 2000

# Run benchmark without plotting
qrngsim benchmark --no-plot

# Save plot to file
qrngsim benchmark -o results.png

# Generate random bits using quantum simulator
qrngsim generate -m quantum -b 256

# Generate bits in hexadecimal format
qrngsim generate -m classical -b 128 --hex

# Save output to file
qrngsim generate -m quantum -b 1024 -o random_bits.txt
```

### In Jupyter Notebook

```python
# Import the package
from qrngsim import *

# Run benchmarks
results = run_benchmark(target_bits=2000)

# Visualize results
plot_results(results)
plot_speed_comparison(results, target_bits=2000)

# Analyze bit distribution
bits = QuantumSimulatorRNG().generate_bits(10000)
plot_bit_distribution(bits, title="Quantum RNG Distribution")
```

## 📁 Project Structure

```
qrngsim/
├── qrngsim/                    # Main package
│   ├── __init__.py            # Package exports
│   ├── cli.py                 # Command-line interface
│   ├── benchmark.py           # Benchmarking engine
│   ├── visualization.py       # Plotting utilities
│   └── generators/            # RNG implementations
│       ├── __init__.py
│       ├── base.py            # Abstract base class
│       ├── quantum_simulator.py
│       ├── anu_api.py
│       └── classical.py
├── tests/                      # Unit tests
│   ├── test_generators.py
│   └── test_benchmark.py
├── notebooks/                  # Jupyter notebooks
│   └── QRNG_Simulation.ipynb
├── pyproject.toml             # Project configuration
├── requirements.txt           # Dependencies
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=qrngsim --cov-report=html

# Run specific test file
pytest tests/test_generators.py

# Run with verbose output
pytest -v
```

## 🔬 How It Works

### Quantum Simulation (Qiskit)
Uses a single qubit put into superposition via a Hadamard gate. Each measurement collapses the superposition, yielding a truly random 0 or 1 (within simulation accuracy).

```
|0⟩ → H → |+⟩ = (|0⟩ + |1⟩)/√2 → Measure → 0 or 1 (50% each)
```

### ANU Quantum API
Connects to the Australian National University's quantum random number server, which generates true random numbers from quantum vacuum fluctuations measured in real-time.

### Classical (Python secrets)
Uses the operating system's cryptographically secure pseudo-random number generator as a baseline for comparison.

## 📊 Example Output

```
--- Benchmarking Generation of 1024 bits ---
Method               | Time (sec) | Speed (bits/s)
--------------------------------------------------
Local Qiskit Sim     | 0.04521 s  | 22649
Classical OS         | 0.00012 s  | 8533333
Remote ANU API       | 0.45123 s  | 2269
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Qiskit](https://qiskit.org/) - IBM's open-source quantum computing framework
- [ANU Quantum Random Numbers](https://qrng.anu.edu.au/) - Australian National University's QRNG service
- Final Year Project - Your University

## 📚 References

- [Qiskit Documentation](https://docs.quantum.ibm.com/)
- [ANU QRNG API](https://qrng.anu.edu.au/API/api-demo.php)
- [Quantum Random Number Generation](https://en.wikipedia.org/wiki/Quantum_random_number_generator)
