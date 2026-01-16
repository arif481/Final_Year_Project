"""Unit tests for random number generators."""

import pytest
from unittest.mock import patch, MagicMock

from qrngsim.generators import QuantumSimulatorRNG, ClassicalRNG, AnuWebQRNG
from qrngsim.generators.base import BaseRNG


class TestBaseRNG:
    """Tests for the BaseRNG abstract class."""
    
    def test_cannot_instantiate_base_class(self):
        """BaseRNG should not be directly instantiable."""
        with pytest.raises(TypeError):
            BaseRNG()


class TestQuantumSimulatorRNG:
    """Tests for the QuantumSimulatorRNG class."""
    
    @pytest.fixture
    def quantum_rng(self):
        """Create a QuantumSimulatorRNG instance."""
        return QuantumSimulatorRNG()
    
    def test_initialization(self, quantum_rng):
        """Test that the quantum RNG initializes correctly."""
        assert quantum_rng.backend is not None
    
    def test_generate_bits_returns_string(self, quantum_rng):
        """Test that generate_bits returns a string."""
        result = quantum_rng.generate_bits(10)
        assert isinstance(result, str)
    
    def test_generate_bits_correct_length(self, quantum_rng):
        """Test that generate_bits returns correct number of bits."""
        for num_bits in [1, 10, 100, 256]:
            result = quantum_rng.generate_bits(num_bits)
            assert len(result) == num_bits
    
    def test_generate_bits_only_binary(self, quantum_rng):
        """Test that generate_bits returns only 0s and 1s."""
        result = quantum_rng.generate_bits(100)
        assert all(c in '01' for c in result)
    
    def test_generate_zero_bits(self, quantum_rng):
        """Test generating zero bits returns empty string."""
        result = quantum_rng.generate_bits(0)
        assert result == ""
    
    def test_generate_negative_bits(self, quantum_rng):
        """Test generating negative bits returns empty string."""
        result = quantum_rng.generate_bits(-5)
        assert result == ""
    
    def test_randomness_distribution(self, quantum_rng):
        """Test that the distribution is roughly 50/50."""
        bits = quantum_rng.generate_bits(10000)
        zeros = bits.count('0')
        ones = bits.count('1')
        # Allow 10% deviation from 50/50
        assert 4000 < zeros < 6000
        assert 4000 < ones < 6000


class TestClassicalRNG:
    """Tests for the ClassicalRNG class."""
    
    @pytest.fixture
    def classical_rng(self):
        """Create a ClassicalRNG instance."""
        return ClassicalRNG()
    
    def test_generate_bits_returns_string(self, classical_rng):
        """Test that generate_bits returns a string."""
        result = classical_rng.generate_bits(10)
        assert isinstance(result, str)
    
    def test_generate_bits_correct_length(self, classical_rng):
        """Test that generate_bits returns correct number of bits."""
        for num_bits in [1, 10, 100, 256, 1024]:
            result = classical_rng.generate_bits(num_bits)
            assert len(result) == num_bits
    
    def test_generate_bits_only_binary(self, classical_rng):
        """Test that generate_bits returns only 0s and 1s."""
        result = classical_rng.generate_bits(100)
        assert all(c in '01' for c in result)
    
    def test_generate_zero_bits(self, classical_rng):
        """Test generating zero bits returns empty string."""
        result = classical_rng.generate_bits(0)
        assert result == ""
    
    def test_randomness_distribution(self, classical_rng):
        """Test that the distribution is roughly 50/50."""
        bits = classical_rng.generate_bits(10000)
        zeros = bits.count('0')
        ones = bits.count('1')
        assert 4000 < zeros < 6000
        assert 4000 < ones < 6000


class TestAnuWebQRNG:
    """Tests for the AnuWebQRNG class."""
    
    @pytest.fixture
    def anu_rng(self):
        """Create an AnuWebQRNG instance."""
        return AnuWebQRNG()
    
    def test_initialization(self, anu_rng):
        """Test that the ANU RNG initializes with correct URL."""
        assert "qrng.anu.edu.au" in anu_rng.url
    
    def test_custom_timeout(self):
        """Test that custom timeout is set."""
        rng = AnuWebQRNG(timeout=30)
        assert rng.timeout == 30
    
    @patch('qrngsim.generators.anu_api.requests.get')
    def test_generate_bits_success(self, mock_get, anu_rng):
        """Test successful bit generation with mocked API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": [255, 128, 64, 32]  # Some random bytes
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = anu_rng.generate_bits(16)
        
        assert isinstance(result, str)
        assert len(result) == 16
        assert all(c in '01' for c in result)
    
    @patch('qrngsim.generators.anu_api.requests.get')
    def test_generate_bits_timeout(self, mock_get, anu_rng):
        """Test handling of timeout errors."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(ConnectionError):
            anu_rng.generate_bits(10)
    
    @patch('qrngsim.generators.anu_api.requests.get')
    def test_generate_bits_connection_error(self, mock_get, anu_rng):
        """Test handling of connection errors."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(ConnectionError):
            anu_rng.generate_bits(10)
    
    def test_generate_zero_bits(self, anu_rng):
        """Test generating zero bits returns empty string."""
        result = anu_rng.generate_bits(0)
        assert result == ""


class TestGenerateBytes:
    """Tests for the generate_bytes method."""
    
    def test_classical_generate_bytes(self):
        """Test generating bytes with classical RNG."""
        rng = ClassicalRNG()
        result = rng.generate_bytes(10)
        assert isinstance(result, bytes)
        assert len(result) == 10
    
    def test_quantum_generate_bytes(self):
        """Test generating bytes with quantum RNG."""
        rng = QuantumSimulatorRNG()
        result = rng.generate_bytes(10)
        assert isinstance(result, bytes)
        assert len(result) == 10


class TestGenerateInt:
    """Tests for the generate_int method."""
    
    def test_generate_int_in_range(self):
        """Test that generated integers are in the specified range."""
        rng = ClassicalRNG()
        for _ in range(100):
            value = rng.generate_int(0, 100)
            assert 0 <= value <= 100
    
    def test_generate_int_custom_range(self):
        """Test generating integers with custom range."""
        rng = ClassicalRNG()
        for _ in range(50):
            value = rng.generate_int(50, 60)
            assert 50 <= value <= 60
