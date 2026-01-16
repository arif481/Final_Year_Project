"""
QRNG Simulation Package
=======================

A Python package for comparing Quantum Random Number Generation methods:
- Local quantum simulation using Qiskit
- Remote true quantum via ANU API
- Classical baseline using Python secrets

Usage:
    from qrngsim import QuantumSimulatorRNG, AnuWebQRNG, ClassicalRNG
    from qrngsim import run_benchmark, plot_results
"""

from qrngsim.generators.quantum_simulator import QuantumSimulatorRNG
from qrngsim.generators.anu_api import AnuWebQRNG
from qrngsim.generators.classical import ClassicalRNG
from qrngsim.benchmark import run_benchmark
from qrngsim.visualization import plot_results

__version__ = "0.1.0"
__author__ = "Your Name"

__all__ = [
    "QuantumSimulatorRNG",
    "AnuWebQRNG", 
    "ClassicalRNG",
    "run_benchmark",
    "plot_results",
]
