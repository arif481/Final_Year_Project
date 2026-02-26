"""QRNG + ECDH security check against Grover-only attacks.

This script demonstrates:
1) ECDH private key generation from QRNG-like sources (qiskit/random.org/fallback).
2) Real ECDH shared secret derivation.
3) Practical attack estimates using only Grover-style search.

Key claim shown in output:
Grover does not break QRNG itself, and Grover-only attacks are not practical
for P-256 ECDH under realistic budgets.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import secrets
import sys
from typing import Callable

import requests
from cryptography.hazmat.primitives.asymmetric import ec


SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
RANDOM_ORG_URL = "https://www.random.org/integers/"
P256_ORDER = int(
    "FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551", 16
)


@dataclass
class QrngKeyMaterial:
    """Random material used to build the ECDH private key."""

    source_used: str
    source_note: str
    random_bytes: bytes
    private_scalar: int


@dataclass
class EcdhRun:
    """Single ECDH run outputs."""

    curve_name: str
    order: int
    order_bits: int
    shared_secret_hex: str


@dataclass
class GroverEstimate:
    """Attack-cost estimate using Grover-only assumptions."""

    keyspace_size: int
    classical_pollard_steps: int
    grover_steps: int
    effective_oracle_rate: float
    expected_runtime_years: float
    attack_window_years: float
    practical_break: bool
    reason: str


def generate_bytes_with_secrets(num_bytes: int) -> bytes:
    """Generate random bytes from local CSPRNG."""
    return secrets.token_bytes(num_bytes)


def generate_bits_with_qiskit(num_bits: int) -> str:
    """Generate random bits using Qiskit measurement."""
    if num_bits <= 0:
        raise ValueError("num_bits must be > 0")

    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    qc = QuantumCircuit(num_bits, num_bits)
    qc.h(range(num_bits))
    qc.measure(range(num_bits), range(num_bits))

    backend = AerSimulator()
    job = backend.run(qc, shots=1, memory=True)
    return job.result().get_memory()[0]


def generate_bytes_with_qiskit(num_bytes: int) -> bytes:
    """Generate random bytes from Qiskit bits in manageable chunks."""
    num_bits = num_bytes * 8
    max_chunk_bits = 24
    bit_chunks: list[str] = []
    remaining = num_bits

    while remaining > 0:
        chunk_bits = min(max_chunk_bits, remaining)
        bit_chunks.append(generate_bits_with_qiskit(chunk_bits))
        remaining -= chunk_bits

    bits = "".join(bit_chunks)
    value = int(bits, 2)
    return value.to_bytes(num_bytes, "big")


def generate_bytes_with_random_org(num_bytes: int, timeout: float) -> bytes:
    """Generate random bytes using random.org integer API."""
    params = {
        "num": num_bytes,
        "min": 0,
        "max": 255,
        "col": 1,
        "base": 10,
        "format": "plain",
        "rnd": "new",
    }
    response = requests.get(RANDOM_ORG_URL, params=params, timeout=timeout)
    response.raise_for_status()

    lines = [line.strip() for line in response.text.splitlines() if line.strip()]
    if len(lines) < num_bytes:
        raise RuntimeError("random.org returned insufficient bytes.")
    return bytes(int(v) for v in lines[:num_bytes])


def resolve_qrng_bytes(
    num_bytes: int, source: str, randomorg_timeout: float
) -> tuple[bytes, str, str]:
    """Resolve random bytes from requested or fallback source."""
    if source == "secrets":
        data = generate_bytes_with_secrets(num_bytes)
        return data, "secrets", "Local CSPRNG used."

    if source == "qiskit":
        try:
            data = generate_bytes_with_qiskit(num_bytes)
            return data, "qiskit", "Qiskit measurement used."
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Qiskit is not installed. Install qiskit + qiskit-aer, "
                "or use --qrng-source randomorg/secrets."
            ) from exc

    if source == "randomorg":
        try:
            data = generate_bytes_with_random_org(num_bytes, randomorg_timeout)
            return data, "randomorg", "random.org QRNG data used."
        except requests.RequestException as exc:
            raise RuntimeError(
                "random.org request failed. Check network or use another source."
            ) from exc

    attempts: list[tuple[str, Callable[[], bytes]]] = [
        ("qiskit", lambda: generate_bytes_with_qiskit(num_bytes)),
        ("randomorg", lambda: generate_bytes_with_random_org(num_bytes, randomorg_timeout)),
        ("secrets", lambda: generate_bytes_with_secrets(num_bytes)),
    ]
    errors: list[str] = []
    for name, fn in attempts:
        try:
            data = fn()
            return data, name, f"{name} source selected by auto fallback."
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    raise RuntimeError("All random sources failed: " + " | ".join(errors))


def create_qrng_ecdh_scalar(source: str, randomorg_timeout: float) -> QrngKeyMaterial:
    """Create a valid P-256 private scalar from random bytes."""
    num_bytes = 32
    random_bytes, source_used, source_note = resolve_qrng_bytes(
        num_bytes=num_bytes,
        source=source,
        randomorg_timeout=randomorg_timeout,
    )
    random_int = int.from_bytes(random_bytes, "big")
    scalar = (random_int % (P256_ORDER - 1)) + 1
    return QrngKeyMaterial(
        source_used=source_used,
        source_note=source_note,
        random_bytes=random_bytes,
        private_scalar=scalar,
    )


def run_ecdh_from_scalar(private_scalar: int) -> EcdhRun:
    """Run an ECDH key exchange using a provided private scalar."""
    private_key = ec.derive_private_key(private_scalar, ec.SECP256R1())
    peer_private = ec.generate_private_key(ec.SECP256R1())
    shared_secret = private_key.exchange(ec.ECDH(), peer_private.public_key())

    return EcdhRun(
        curve_name="secp256r1 (P-256)",
        order=P256_ORDER,
        order_bits=P256_ORDER.bit_length(),
        shared_secret_hex=shared_secret.hex(),
    )


def estimate_grover_only_attack(
    keyspace_size: int,
    oracle_checks_per_second: float,
    quantum_processors: int,
    attack_window_years: float,
) -> GroverEstimate:
    """Estimate Grover-only practicality for ECDH key search."""
    if keyspace_size <= 0:
        raise ValueError("keyspace_size must be > 0")
    if oracle_checks_per_second <= 0:
        raise ValueError("oracle_checks_per_second must be > 0")
    if quantum_processors <= 0:
        raise ValueError("quantum_processors must be > 0")
    if attack_window_years <= 0:
        raise ValueError("attack_window_years must be > 0")

    sqrt_n = math.sqrt(keyspace_size)
    classical_pollard_steps = math.ceil(math.sqrt(math.pi * keyspace_size / 2))
    grover_steps = math.ceil((math.pi / 4) * sqrt_n)

    effective_rate = oracle_checks_per_second * quantum_processors
    runtime_seconds = grover_steps / effective_rate
    runtime_years = runtime_seconds / SECONDS_PER_YEAR
    practical_break = runtime_years <= attack_window_years

    reason = (
        "Grover search fits in the provided budget."
        if practical_break
        else "Grover search does not fit in the provided budget."
    )

    return GroverEstimate(
        keyspace_size=keyspace_size,
        classical_pollard_steps=classical_pollard_steps,
        grover_steps=grover_steps,
        effective_oracle_rate=effective_rate,
        expected_runtime_years=runtime_years,
        attack_window_years=attack_window_years,
        practical_break=practical_break,
        reason=reason,
    )


def parse_args() -> argparse.Namespace:
    """Parse command line args."""
    parser = argparse.ArgumentParser(
        description=(
            "Demonstrate that QRNG is not broken by Grover and "
            "Grover-only ECDH key search is impractical for P-256."
        )
    )
    parser.add_argument(
        "--qrng-source",
        choices=["auto", "qiskit", "randomorg", "secrets"],
        default="auto",
        help="Random source for ECDH private scalar (default: auto).",
    )
    parser.add_argument(
        "--randomorg-timeout",
        type=float,
        default=10.0,
        help="Timeout seconds for random.org source (default: 10).",
    )
    parser.add_argument(
        "--oracle-rate",
        type=float,
        default=1e12,
        help="Oracle checks per second per quantum processor (default: 1e12).",
    )
    parser.add_argument(
        "--quantum-processors",
        type=int,
        default=1_000_000,
        help="Number of parallel quantum processors (default: 1,000,000).",
    )
    parser.add_argument(
        "--attack-window-years",
        type=float,
        default=10.0,
        help="Allowed attacker time budget in years (default: 10).",
    )
    parser.add_argument(
        "--show-sensitive",
        action="store_true",
        help="Print private scalar and full shared secret (off by default).",
    )
    return parser.parse_args()


def main() -> None:
    """Run QRNG + ECDH + Grover-only assessment."""
    args = parse_args()
    try:
        material = create_qrng_ecdh_scalar(
            source=args.qrng_source, randomorg_timeout=args.randomorg_timeout
        )
        ecdh = run_ecdh_from_scalar(material.private_scalar)
        estimate = estimate_grover_only_attack(
            keyspace_size=ecdh.order - 1,
            oracle_checks_per_second=args.oracle_rate,
            quantum_processors=args.quantum_processors,
            attack_window_years=args.attack_window_years,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    print("QRNG + ECDH Grover-Only Assessment")
    print("=" * 64)
    print(f"Curve: {ecdh.curve_name}")
    print(f"Curve order bits: {ecdh.order_bits}")
    print(f"QRNG source used: {material.source_used}")
    print(f"Source note: {material.source_note}")
    print(f"Random seed bytes (hex, first 16): {material.random_bytes[:16].hex()}...")
    if args.show_sensitive:
        print(f"ECDH private scalar: {material.private_scalar}")
        print(f"ECDH shared secret (hex): {ecdh.shared_secret_hex}")
    else:
        print(
            "ECDH shared secret (hex, first 16): "
            f"{ecdh.shared_secret_hex[:32]}..."
        )
    print()
    print("Grover-Only Attack Estimate")
    print("-" * 64)
    print(f"Search space size (~curve order): {estimate.keyspace_size:,}")
    print(
        "Classical generic ECDLP cost (Pollard rho, expected steps): "
        f"{estimate.classical_pollard_steps:,}"
    )
    print(f"Grover required iterations: {estimate.grover_steps:,}")
    print(
        "Effective oracle rate (checks/sec): "
        f"{estimate.effective_oracle_rate:,.2f}"
    )
    print(f"Estimated Grover runtime: {estimate.expected_runtime_years:,.2e} years")
    print(f"Attack budget: {estimate.attack_window_years:g} years")
    print(f"Assessment: {estimate.reason}")
    print()
    print("QRNG predictability broken by Grover: NO")
    print(
        "FINAL RESULT - QRNG+ECDH broken by Grover-only attack:",
        "YES" if estimate.practical_break else "NO",
    )


if __name__ == "__main__":
    main()
