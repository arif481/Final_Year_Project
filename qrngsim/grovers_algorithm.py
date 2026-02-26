"""Input-driven Grover/classical key-search demonstration.

This module demonstrates:
1) Encrypting input text with a toy XOR key cipher.
2) "Breaking" the ciphertext using classical brute-force key search.
3) Reporting measured iteration timing on a classical computer.
4) Estimating Grover iteration count for the same keyspace.

The final output line always states whether the attack broke encryption.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import secrets
import time


@dataclass
class AttackSetup:
    """Parameters for the encryption and attack run."""

    key_bits: int
    secret_key: int
    ciphertext: bytes
    known_prefix: bytes


@dataclass
class ClassicalAttackResult:
    """Result of classical brute-force search."""

    keyspace_size: int
    iterations_tested: int
    elapsed_seconds: float
    iterations_per_second: float
    estimated_full_scan_seconds: float
    estimated_average_break_seconds: float
    broken: bool
    recovered_key: int | None
    recovered_plaintext: bytes | None


def xor_cipher(data: bytes, key: int, key_bits: int) -> bytes:
    """Encrypt/decrypt bytes using repeating-key XOR from integer key."""
    if key_bits <= 0:
        raise ValueError("key_bits must be > 0")
    if key < 0:
        raise ValueError("key must be >= 0")

    key_len = max(1, (key_bits + 7) // 8)
    key_bytes = key.to_bytes(key_len, byteorder="big", signed=False)
    return bytes(b ^ key_bytes[i % key_len] for i, b in enumerate(data))


def grover_iteration_estimate(keyspace_size: int) -> int:
    """Estimate Grover iterations for one marked solution."""
    if keyspace_size <= 0:
        raise ValueError("keyspace_size must be > 0")
    return math.ceil((math.pi / 4) * math.sqrt(keyspace_size))


def brute_force_xor_key(
    ciphertext: bytes,
    known_prefix: bytes,
    key_bits: int,
    max_iterations: int | None = None,
) -> ClassicalAttackResult:
    """Try all keys until plaintext prefix matches, measuring timing."""
    keyspace_size = 1 << key_bits
    iteration_limit = keyspace_size if max_iterations is None else min(max_iterations, keyspace_size)

    start = time.perf_counter()
    found_key: int | None = None
    found_plaintext: bytes | None = None

    for key in range(iteration_limit):
        candidate = xor_cipher(ciphertext, key, key_bits)
        if candidate.startswith(known_prefix):
            found_key = key
            found_plaintext = candidate
            break

    elapsed = time.perf_counter() - start
    tested = key + 1 if iteration_limit > 0 else 0
    if found_key is None and iteration_limit > 0:
        tested = iteration_limit

    rate = (tested / elapsed) if elapsed > 0 and tested > 0 else 0.0
    est_full = (keyspace_size / rate) if rate > 0 else float("inf")
    est_avg = est_full / 2 if math.isfinite(est_full) else float("inf")

    return ClassicalAttackResult(
        keyspace_size=keyspace_size,
        iterations_tested=tested,
        elapsed_seconds=elapsed,
        iterations_per_second=rate,
        estimated_full_scan_seconds=est_full,
        estimated_average_break_seconds=est_avg,
        broken=found_key is not None,
        recovered_key=found_key,
        recovered_plaintext=found_plaintext,
    )


def format_seconds(seconds: float) -> str:
    """Format seconds into a readable duration string."""
    if not math.isfinite(seconds):
        return "infinite"

    minute = 60
    hour = 60 * minute
    day = 24 * hour
    year = 365.25 * day

    if seconds < minute:
        return f"{seconds:.6f} s"
    if seconds < hour:
        return f"{seconds / minute:.4f} min"
    if seconds < day:
        return f"{seconds / hour:.4f} h"
    if seconds < year:
        return f"{seconds / day:.4f} days"
    return f"{seconds / year:.4f} years"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run an input-driven classical key-search break and Grover estimate."
    )
    parser.add_argument(
        "--message",
        type=str,
        default=None,
        help="Plaintext message to encrypt first (if omitted, interactive prompt is used).",
    )
    parser.add_argument(
        "--known-prefix",
        type=str,
        default=None,
        help="Known plaintext prefix used for key validation.",
    )
    parser.add_argument(
        "--key-bits",
        type=int,
        default=16,
        help="Key size for toy cipher brute force (default: 16).",
    )
    parser.add_argument(
        "--key",
        type=str,
        default=None,
        help="Secret key as int (supports 0x...); if omitted, random key is used.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Optional cap on tested keys.",
    )
    return parser.parse_args()


def collect_input(args: argparse.Namespace) -> AttackSetup:
    """Build attack setup from args or interactive input."""
    key_bits = args.key_bits
    if key_bits <= 0:
        raise ValueError("key_bits must be > 0")

    keyspace_size = 1 << key_bits

    message = args.message
    if message is None:
        message = input("Enter message to encrypt and attack: ").strip()
        if not message:
            raise ValueError("message cannot be empty")

    if args.key is None:
        secret_key = secrets.randbelow(keyspace_size)
    else:
        secret_key = int(args.key, 0)
        if secret_key < 0 or secret_key >= keyspace_size:
            raise ValueError(f"key must be in range [0, {keyspace_size - 1}]")

    plaintext = message.encode("utf-8")
    ciphertext = xor_cipher(plaintext, secret_key, key_bits)

    known_prefix_text = args.known_prefix
    if known_prefix_text is None:
        prefix_len = 4 if len(message) >= 4 else len(message)
        known_prefix_text = message[:prefix_len]
    known_prefix = known_prefix_text.encode("utf-8")

    if not known_prefix:
        raise ValueError("known prefix cannot be empty")

    return AttackSetup(
        key_bits=key_bits,
        secret_key=secret_key,
        ciphertext=ciphertext,
        known_prefix=known_prefix,
    )


def main() -> None:
    """Run encryption, classical break, and Grover iteration estimate."""
    args = parse_args()
    setup = collect_input(args)

    if setup.key_bits > 28 and args.max_iterations is None:
        print("Large key size detected; auto-capping to 5,000,000 iterations.")
        max_iterations = 5_000_000
    else:
        max_iterations = args.max_iterations

    result = brute_force_xor_key(
        ciphertext=setup.ciphertext,
        known_prefix=setup.known_prefix,
        key_bits=setup.key_bits,
        max_iterations=max_iterations,
    )

    grover_iters = grover_iteration_estimate(result.keyspace_size)
    grover_time_on_same_rate = (
        grover_iters / result.iterations_per_second
        if result.iterations_per_second > 0
        else float("inf")
    )

    print("Grover + Classical Key-Search Report")
    print("-" * 55)
    print(f"Key bits: {setup.key_bits}")
    print(f"Keyspace size: {result.keyspace_size:,}")
    print(f"Ciphertext (hex): {setup.ciphertext.hex()}")
    print(f"Known prefix used for attack: {setup.known_prefix.decode('utf-8', errors='replace')}")
    print()
    print("Classical brute-force timing")
    print("-" * 55)
    print(f"Iterations tested: {result.iterations_tested:,}")
    print(f"Measured attack time: {format_seconds(result.elapsed_seconds)}")
    print(f"Iteration rate (classical CPU): {result.iterations_per_second:,.2f} keys/s")
    print(f"Estimated full keyspace scan time: {format_seconds(result.estimated_full_scan_seconds)}")
    print(f"Estimated average break time: {format_seconds(result.estimated_average_break_seconds)}")
    print()
    print("Grover iteration estimate")
    print("-" * 55)
    print(f"Estimated Grover iterations: {grover_iters:,}")
    print(
        "Estimated time for that many iterations at same classical rate:",
        format_seconds(grover_time_on_same_rate),
    )
    print()

    if result.broken:
        recovered_text = result.recovered_plaintext.decode("utf-8", errors="replace")
        print(f"Recovered key: {result.recovered_key}")
        print(f"Recovered plaintext: {recovered_text}")
    else:
        print("No key found in the tested iteration range.")

    print()
    print("FINAL RESULT - Encryption broken by classical attack:",
          "YES" if result.broken else "NO")


if __name__ == "__main__":
    main()
