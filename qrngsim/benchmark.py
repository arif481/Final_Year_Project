"""Benchmarking engine for comparing RNG methods."""

import time
from typing import Dict, Optional, List
from dataclasses import dataclass

from qrngsim.generators import QuantumSimulatorRNG, AnuWebQRNG, ClassicalRNG
from qrngsim.generators.base import BaseRNG


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    name: str
    num_bits: int
    duration: float
    speed: float  # bits per second
    success: bool
    error_message: Optional[str] = None
    
    def __str__(self) -> str:
        if self.success:
            return f"{self.name}: {self.duration:.5f}s ({self.speed:.0f} bits/s)"
        return f"{self.name}: FAILED - {self.error_message}"


def get_default_generators() -> Dict[str, BaseRNG]:
    """Get the default set of RNG generators for benchmarking.
    
    Returns:
        Dictionary mapping generator names to instances.
    """
    return {
        "Local Qiskit Sim": QuantumSimulatorRNG(),
        "Classical OS": ClassicalRNG(),
        "Remote ANU API": AnuWebQRNG()
    }


def benchmark_generator(
    generator: BaseRNG,
    name: str,
    num_bits: int
) -> BenchmarkResult:
    """Benchmark a single generator.
    
    Args:
        generator: The RNG instance to benchmark.
        name: Name identifier for the generator.
        num_bits: Number of bits to generate.
        
    Returns:
        BenchmarkResult with timing information.
    """
    try:
        start_time = time.perf_counter()
        bits = generator.generate_bits(num_bits)
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        speed = num_bits / duration if duration > 0 else float('inf')
        
        return BenchmarkResult(
            name=name,
            num_bits=num_bits,
            duration=duration,
            speed=speed,
            success=True
        )
        
    except Exception as e:
        return BenchmarkResult(
            name=name,
            num_bits=num_bits,
            duration=0,
            speed=0,
            success=False,
            error_message=str(e)
        )


def run_benchmark(
    target_bits: int = 1024,
    generators: Optional[Dict[str, BaseRNG]] = None,
    verbose: bool = True
) -> Dict[str, float]:
    """Run benchmarks on all generators.
    
    Args:
        target_bits: Number of bits to generate for each test.
        generators: Optional custom dictionary of generators.
                   Uses default generators if not provided.
        verbose: Whether to print results to console.
        
    Returns:
        Dictionary mapping generator names to their generation times.
    """
    if generators is None:
        generators = get_default_generators()
    
    results: Dict[str, float] = {}
    
    if verbose:
        print(f"\n--- Benchmarking Generation of {target_bits} bits ---")
        print(f"{'Method':<20} | {'Time (sec)':<10} | {'Speed (bits/s)':<15}")
        print("-" * 50)
    
    for name, gen in generators.items():
        result = benchmark_generator(gen, name, target_bits)
        
        if result.success:
            results[name] = result.duration
            if verbose:
                print(f"{name:<20} | {result.duration:.5f} s  | {result.speed:.0f}")
        else:
            if verbose:
                print(f"{name:<20} | FAILED     | {result.error_message}")
    
    return results


def run_detailed_benchmark(
    target_bits: int = 1024,
    generators: Optional[Dict[str, BaseRNG]] = None,
    iterations: int = 1
) -> List[BenchmarkResult]:
    """Run detailed benchmarks with multiple iterations.
    
    Args:
        target_bits: Number of bits to generate for each test.
        generators: Optional custom dictionary of generators.
        iterations: Number of times to run each benchmark.
        
    Returns:
        List of all benchmark results.
    """
    if generators is None:
        generators = get_default_generators()
    
    all_results = []
    
    for _ in range(iterations):
        for name, gen in generators.items():
            result = benchmark_generator(gen, name, target_bits)
            all_results.append(result)
    
    return all_results
