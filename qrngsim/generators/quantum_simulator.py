"""Local Quantum Simulation using Qiskit."""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from qrngsim.generators.base import BaseRNG


class QuantumSimulatorRNG(BaseRNG):
    """Random number generator using local quantum simulation.
    
    Uses Qiskit's AerSimulator to simulate quantum measurements of qubits
    in superposition, producing truly random bits (within simulation limits).
    
    Example:
        >>> rng = QuantumSimulatorRNG()
        >>> bits = rng.generate_bits(100)
        >>> print(len(bits))
        100
    """
    
    def __init__(self):
        """Initialize the quantum simulator backend."""
        self.backend = AerSimulator()
    
    def generate_bits(self, num_bits: int) -> str:
        """Generate random bits using quantum simulation.
        
        Creates a quantum circuit with a single qubit in superposition
        (using Hadamard gate) and measures it multiple times.
        
        Args:
            num_bits: Number of random bits to generate.
            
        Returns:
            A string of '0's and '1's representing the random bits.
        """
        if num_bits <= 0:
            return ""
            
        qc = QuantumCircuit(1, 1)
        qc.h(0)  # Apply Hadamard gate for superposition
        qc.measure(0, 0)
        
        job = self.backend.run(qc, shots=num_bits, memory=True)
        result = job.result()
        memory = result.get_memory()
        
        return "".join(memory)
