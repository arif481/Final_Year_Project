"""Remote True Quantum RNG using ANU API."""

import requests

from qrngsim.generators.base import BaseRNG


class AnuWebQRNG(BaseRNG):
    """Random number generator using ANU Quantum Random Numbers API.
    
    Connects to the Australian National University's quantum random
    number server, which generates true random numbers from quantum
    vacuum fluctuations.
    
    Note:
        Requires internet connection. May be slower than local methods
        due to network latency.
    
    Example:
        >>> rng = AnuWebQRNG()
        >>> bits = rng.generate_bits(100)
        >>> print(len(bits))
        100
    """
    
    API_URL = "https://qrng.anu.edu.au/API/jsonI.php"
    DEFAULT_TIMEOUT = 10
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """Initialize the ANU QRNG client.
        
        Args:
            timeout: Request timeout in seconds (default: 10).
        """
        self.url = self.API_URL
        self.timeout = timeout
    
    def generate_bits(self, num_bits: int) -> str:
        """Generate random bits from ANU quantum server.
        
        Args:
            num_bits: Number of random bits to generate.
            
        Returns:
            A string of '0's and '1's representing the random bits.
            
        Raises:
            ConnectionError: If unable to connect to the API.
            ValueError: If the API returns invalid data.
        """
        if num_bits <= 0:
            return ""
            
        num_bytes = (num_bits // 8) + 1
        params = {
            "length": num_bytes,
            "type": "uint8"
        }
        
        try:
            response = requests.get(self.url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("success"):
                raise ValueError(f"API returned error: {data}")
                
            random_data = data["data"]
            binary_string = "".join(f"{x:08b}" for x in random_data)
            return binary_string[:num_bits]
            
        except requests.exceptions.Timeout:
            raise ConnectionError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to ANU API: {e}")
