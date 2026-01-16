"""Classical Random Number Generator using Python secrets."""

import secrets

from qrngsim.generators.base import BaseRNG


class ClassicalRNG(BaseRNG):
    """Random number generator using Python's secrets module.
    
    Uses the operating system's cryptographically secure random number
    generator. This serves as a baseline for comparing quantum methods.
    
    Example:
        >>> rng = ClassicalRNG()
        >>> bits = rng.generate_bits(100)
        >>> print(len(bits))
        100
    """
    
    def generate_bits(self, num_bits: int) -> str:
        """Generate random bits using OS cryptographic RNG.
        
        Args:
            num_bits: Number of random bits to generate.
            
        Returns:
            A string of '0's and '1's representing the random bits.
        """
        if num_bits <= 0:
            return ""
            
        num_bytes = (num_bits // 8) + 1
        random_bytes = secrets.token_bytes(num_bytes)
        
        binary_string = "".join(f"{x:08b}" for x in random_bytes)
        return binary_string[:num_bits]
