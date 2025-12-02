import argparse
import math
import re
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt

PAIR_RE = re.compile(r"literals(?P<literals>\d+)_clauses(?P<clauses>\d+)")


def read_numbers(path: Path) -> List[float]:
    return [float(line.strip()) for line in path.read_text().splitlines() if line.strip()]


def compute_mae(truth: List[float], pred: List[float]) -> float:
    if not truth or not pred:
        return math.nan
    if len(truth) != len(pred):
        # Align lengths conservatively to avoid mis-shaped data.
        length = min(len(truth), len(pred))
        truth = truth[:length]
        pred = pred[:length]
    return sum(abs(t - p) for t, p in zip(truth, pred)) / len(truth)


def collect_pairs(sol_dir: Path, monte_dir: Path) -> Dict[Tuple[int, int], Dict[str, Path]]:
    pairs: Dict[Tuple[int, int], Dict[str, Path]] = {}
    for sol_path in sol_dir.glob("*_sol.txt"):
        match = PAIR_RE.search(sol_path.name)
        if not match:
            continue
        literals = int(match.group("literals"))
        clauses = int(match.group("clauses"))
        base = sol_path.name.replace("_sol.txt", "")
        eps01 = monte_dir / f"{base}_kl0.10_0.10.txt"
        eps005 = monte_dir / f"{base}_kl0.05_0.05.txt"
        if eps01.exists() and eps005.exists():
            pairs[(literals, clauses)] = {
                "truth": sol_path,
                "eps0.1_delta0.1": eps01,
                "eps0.05_delta0.05": eps005,
            }
    return pairs


def build_mae_table(pairs: Dict[Tuple[int, int], Dict[str, Path]]):
    rows = []
    for (literals, clauses), paths in sorted(pairs.items()):
        truth_vals = read_numbers(paths["truth"])
        mae_01 = compute_mae(truth_vals, read_numbers(paths["eps0.1_delta0.1"]))
        mae_005 = compute_mae(truth_vals, read_numbers(paths["eps0.05_delta0.05"]))
        label = f"L{literals}-C{clauses}"
        rows.append((label, mae_01, mae_005))
    return rows


def plot_mae(rows, output_path: Path | None) -> None:
    labels = [r[0] for r in rows]
    mae_01 = [r[1] for r in rows]
    mae_005 = [r[2] for r in rows]

    x = list(range(len(labels)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars_01 = ax.bar(
        [i - width / 2 for i in x], mae_01, width, label="eps=0.1, delta=0.1"
    )
    bars_005 = ax.bar(
        [i + width / 2 for i in x], mae_005, width, label="eps=0.05, delta=0.05"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("MAE vs ground truth (symlog scale)")
    ax.set_title("MAE comparison for available literal/clause pairs")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    ax.set_yscale("symlog", linthresh=1)
    for bars in (bars_01, bars_005):
        ax.bar_label(bars, fmt="%.3g", padding=2, fontsize=8, rotation=90)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=200)
        print(f"Saved plot to {output_path.resolve()}")
    else:
        plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot MAE against ground truth for eps/delta runs."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save the figure; if omitted, the plot is shown.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "Output",
        help="Directory containing *_sol.txt ground truth files.",
    )
    parser.add_argument(
        "--monte-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory containing Monte Carlo outputs with eps/delta suffixes.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pairs = collect_pairs(args.output_dir, args.monte_dir)
    if not pairs:
        raise SystemExit("No matching literal/clause pairs found in Output directory.")

    rows = build_mae_table(pairs)
    plot_mae(rows, args.output)


if __name__ == "__main__":
    main()
