"""Command-line interface for QRNG Simulation."""

import argparse
import sys

from qrngsim import run_benchmark, plot_results
from qrngsim.generators import QuantumSimulatorRNG, AnuWebQRNG, ClassicalRNG


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="qrngsim",
        description="Quantum Random Number Generator Simulation and Benchmarking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qrngsim benchmark                    Run benchmark with default settings
  qrngsim benchmark -b 2000            Benchmark with 2000 bits
  qrngsim benchmark --no-plot          Run benchmark without plotting
  qrngsim generate -m quantum -b 100   Generate 100 bits using quantum simulator
  qrngsim generate -m classical        Generate bits using classical RNG
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Benchmark command
    bench_parser = subparsers.add_parser(
        "benchmark",
        help="Run benchmarks comparing RNG methods"
    )
    bench_parser.add_argument(
        "-b", "--bits",
        type=int,
        default=1024,
        help="Number of bits to generate (default: 1024)"
    )
    bench_parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip plotting results"
    )
    bench_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Save plot to file (e.g., results.png)"
    )
    
    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate random bits"
    )
    gen_parser.add_argument(
        "-m", "--method",
        choices=["quantum", "classical", "anu"],
        default="quantum",
        help="RNG method to use (default: quantum)"
    )
    gen_parser.add_argument(
        "-b", "--bits",
        type=int,
        default=256,
        help="Number of bits to generate (default: 256)"
    )
    gen_parser.add_argument(
        "--hex",
        action="store_true",
        help="Output in hexadecimal format"
    )
    gen_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Save output to file"
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    if args.command == "benchmark":
        run_benchmark_command(args)
    elif args.command == "generate":
        run_generate_command(args)


def run_benchmark_command(args):
    """Execute the benchmark command."""
    print(f"Running QRNG Benchmark with {args.bits} bits...\n")
    
    results = run_benchmark(target_bits=args.bits, verbose=True)
    
    if not args.no_plot and results:
        plot_results(results, save_path=args.output)


def run_generate_command(args):
    """Execute the generate command."""
    generators = {
        "quantum": QuantumSimulatorRNG,
        "classical": ClassicalRNG,
        "anu": AnuWebQRNG
    }
    
    generator = generators[args.method]()
    
    try:
        bits = generator.generate_bits(args.bits)
        
        if args.hex:
            # Convert to hex
            hex_output = hex(int(bits, 2))[2:].zfill(args.bits // 4)
            output = hex_output
        else:
            output = bits
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Output saved to: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
