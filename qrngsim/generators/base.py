"""Base class for all random number generators."""

from abc import ABC, abstractmethod


class BaseRNG(ABC):
    """Abstract base class for random number generators.
    
    All RNG implementations should inherit from this class and implement
    the generate_bits method.
    """
    
    @abstractmethod
    def generate_bits(self, num_bits: int) -> str:
        """Generate random bits.
        
        Args:
            num_bits: Number of random bits to generate.
            
        Returns:
            A string of '0's and '1's representing the random bits.
        """
        pass
    
    def generate_bytes(self, num_bytes: int) -> bytes:
        """Generate random bytes.
        
        Args:
            num_bytes: Number of random bytes to generate.
            
        Returns:
            Random bytes.
        """
        bits = self.generate_bits(num_bytes * 8)
        return int(bits, 2).to_bytes(num_bytes, byteorder='big')
    
    def generate_int(self, min_val: int = 0, max_val: int = 255) -> int:
        """Generate a random integer in the given range.
        
        Args:
            min_val: Minimum value (inclusive).
            max_val: Maximum value (inclusive).
            
        Returns:
            A random integer in [min_val, max_val].
        """
        range_size = max_val - min_val + 1
        bits_needed = range_size.bit_length()
        
        while True:
            bits = self.generate_bits(bits_needed)
            value = int(bits, 2)
            if value < range_size:
                return min_val + value
