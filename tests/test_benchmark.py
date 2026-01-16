"""Unit tests for benchmark module."""

import pytest
from unittest.mock import MagicMock, patch

from qrngsim.benchmark import (
    BenchmarkResult,
    benchmark_generator,
    run_benchmark,
    get_default_generators
)
from qrngsim.generators import ClassicalRNG


class TestBenchmarkResult:
    """Tests for the BenchmarkResult dataclass."""
    
    def test_successful_result_str(self):
        """Test string representation of successful result."""
        result = BenchmarkResult(
            name="Test",
            num_bits=1000,
            duration=0.5,
            speed=2000,
            success=True
        )
        assert "Test" in str(result)
        assert "0.5" in str(result)
        assert "2000" in str(result)
    
    def test_failed_result_str(self):
        """Test string representation of failed result."""
        result = BenchmarkResult(
            name="Test",
            num_bits=1000,
            duration=0,
            speed=0,
            success=False,
            error_message="Connection failed"
        )
        assert "FAILED" in str(result)
        assert "Connection failed" in str(result)


class TestBenchmarkGenerator:
    """Tests for the benchmark_generator function."""
    
    def test_benchmark_successful(self):
        """Test benchmarking a successful generator."""
        rng = ClassicalRNG()
        result = benchmark_generator(rng, "Classical", 1000)
        
        assert result.success is True
        assert result.name == "Classical"
        assert result.num_bits == 1000
        assert result.duration > 0
        assert result.speed > 0
    
    def test_benchmark_handles_errors(self):
        """Test that benchmark handles generator errors gracefully."""
        mock_rng = MagicMock()
        mock_rng.generate_bits.side_effect = Exception("Test error")
        
        result = benchmark_generator(mock_rng, "Broken", 100)
        
        assert result.success is False
        assert "Test error" in result.error_message


class TestGetDefaultGenerators:
    """Tests for the get_default_generators function."""
    
    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        generators = get_default_generators()
        assert isinstance(generators, dict)
    
    def test_contains_all_generators(self):
        """Test that all expected generators are present."""
        generators = get_default_generators()
        assert len(generators) == 3
        assert "Local Qiskit Sim" in generators
        assert "Classical OS" in generators
        assert "Remote ANU API" in generators


class TestRunBenchmark:
    """Tests for the run_benchmark function."""
    
    def test_returns_dict(self):
        """Test that run_benchmark returns a dictionary."""
        # Use only classical for speed
        generators = {"Classical": ClassicalRNG()}
        result = run_benchmark(target_bits=100, generators=generators, verbose=False)
        
        assert isinstance(result, dict)
    
    def test_custom_generators(self):
        """Test using custom generators."""
        custom_gens = {"Test": ClassicalRNG()}
        result = run_benchmark(target_bits=100, generators=custom_gens, verbose=False)
        
        assert "Test" in result
    
    def test_verbose_output(self, capsys):
        """Test verbose output."""
        generators = {"Classical": ClassicalRNG()}
        run_benchmark(target_bits=100, generators=generators, verbose=True)
        
        captured = capsys.readouterr()
        assert "Benchmarking" in captured.out
        assert "Classical" in captured.out
