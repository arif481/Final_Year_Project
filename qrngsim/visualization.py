"""Visualization utilities for benchmark results."""

from typing import Dict, Optional, List
import matplotlib.pyplot as plt


# Default color scheme
COLORS = ['#6929c4', '#009d9a', '#1192e8', '#fa4d56', '#570408']


def plot_results(
    results: Dict[str, float],
    title: str = "QRNG Simulation Time Comparison",
    save_path: Optional[str] = None,
    colors: Optional[List[str]] = None
) -> None:
    """Plot benchmark results as a bar chart.
    
    Args:
        results: Dictionary mapping method names to generation times.
        title: Chart title.
        save_path: Optional path to save the figure.
        colors: Optional list of bar colors.
    """
    if not results:
        print("No results to plot.")
        return
    
    names = list(results.keys())
    times = list(results.values())
    
    if colors is None:
        colors = COLORS[:len(names)]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, times, color=colors)
    
    plt.ylabel('Time to Generate (Seconds)')
    plt.title(title)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels on bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval,
            f'{yval:.4f}s',
            va='bottom',
            ha='center'
        )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    plt.show()


def plot_speed_comparison(
    results: Dict[str, float],
    target_bits: int = 1024,
    save_path: Optional[str] = None
) -> None:
    """Plot speed comparison (bits per second).
    
    Args:
        results: Dictionary mapping method names to generation times.
        target_bits: Number of bits used in the benchmark.
        save_path: Optional path to save the figure.
    """
    if not results:
        print("No results to plot.")
        return
    
    names = list(results.keys())
    speeds = [target_bits / t if t > 0 else 0 for t in results.values()]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, speeds, color=COLORS[:len(names)])
    
    plt.ylabel('Generation Speed (bits/second)')
    plt.title('QRNG Speed Comparison')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval,
            f'{yval:.0f}',
            va='bottom',
            ha='center'
        )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.show()


def plot_bit_distribution(
    bits: str,
    title: str = "Bit Distribution",
    save_path: Optional[str] = None
) -> None:
    """Plot the distribution of 0s and 1s in a bit string.
    
    Args:
        bits: String of '0's and '1's.
        title: Chart title.
        save_path: Optional path to save the figure.
    """
    zeros = bits.count('0')
    ones = bits.count('1')
    total = len(bits)
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(['0', '1'], [zeros, ones], color=['#6929c4', '#009d9a'])
    
    plt.ylabel('Count')
    plt.xlabel('Bit Value')
    plt.title(f'{title}\n(Total: {total} bits)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add percentage labels
    for bar, count in zip(bars, [zeros, ones]):
        percentage = (count / total) * 100 if total > 0 else 0
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f'{count}\n({percentage:.1f}%)',
            va='bottom',
            ha='center'
        )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.show()
