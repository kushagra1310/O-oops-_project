"""Plot runtime comparison across eps=0.1, eps=0.05, and brute force.

The script builds bar charts per literal count where the x-axis is the number
of clauses and each group has bars for eps=0.1, eps=0.05, and brute force.
Only instances with available brute-force timings are included.
"""

import argparse
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare Monte Carlo and brute-force runtimes.")
    parser.add_argument(
        "--eps01",
        type=Path,
        default=Path(__file__).resolve().parent / "monte_summary_all_eps0.1_delta0.1_latest.csv",
        help="Path to eps=0.1 summary CSV (Monte Carlo).",
    )
    parser.add_argument(
        "--eps005",
        type=Path,
        default=Path(__file__).resolve().parent / "monte_summary_all_eps0.05_delta0.05.csv",
        help="Path to eps=0.05 summary CSV (Monte Carlo).",
    )
    parser.add_argument(
        "--deterministic",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "Output" / "solve_times_literals_le_20.csv",
        help="Path to brute-force timing CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save the plot; if omitted the plot is shown.",
    )
    return parser.parse_args()


def extract_metadata(file_col: pd.Series) -> pd.DataFrame:
    """Extract literal and clause counts from the filename column."""

    meta = file_col.str.extract(r"literals(?P<literals>\d+)_clauses(?P<clauses>\d+)")
    return meta.apply(pd.to_numeric, errors="coerce")


def load_monte(csv_path: Path, label: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = df[df["status"] == "ok"].copy()
    meta = extract_metadata(df["file"])
    df = pd.concat([df, meta], axis=1)
    df = df.dropna(subset=["literals", "clauses"])
    df[["literals", "clauses"]] = df[["literals", "clauses"]].astype(int)
    df = df.rename(columns={"seconds": f"seconds_{label}", "file": f"file_{label}"})
    return df[[f"file_{label}", "literals", "clauses", f"seconds_{label}"]]


def load_bruteforce(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    meta = extract_metadata(df["file"])
    df = pd.concat([df, meta], axis=1)
    df = df.dropna(subset=["literals", "clauses"])
    df[["literals", "clauses"]] = df[["literals", "clauses"]].astype(int)
    df = df.rename(columns={"seconds": "seconds_bruteforce", "file": "file_bruteforce"})
    return df[["file_bruteforce", "literals", "clauses", "seconds_bruteforce"]]


def merge_available(df_bf: pd.DataFrame, df_eps01: pd.DataFrame, df_eps005: pd.DataFrame) -> pd.DataFrame:
    merged = df_bf.merge(df_eps01, on=["literals", "clauses"], how="inner")
    merged = merged.merge(df_eps005, on=["literals", "clauses"], how="inner")
    merged = merged.sort_values(["literals", "clauses"]).reset_index(drop=True)
    return merged


def plot_bars(df: pd.DataFrame, output_path: Optional[Path]) -> None:
    literals_list = sorted(df["literals"].unique())
    n_rows = len(literals_list)
    fig, axes = plt.subplots(n_rows, 1, figsize=(10, 3 * n_rows), sharex=False)
    if n_rows == 1:
        axes = [axes]

    bar_width = 0.25
    for ax, literals in zip(axes, literals_list):
        subset = df[df["literals"] == literals].sort_values("clauses")
        x = range(len(subset))

        ax.bar(
            [xi - bar_width for xi in x],
            subset["seconds_eps01"],
            width=bar_width,
            label="eps=0.1",
        )
        ax.bar(
            x,
            subset["seconds_eps005"],
            width=bar_width,
            label="eps=0.05",
        )
        ax.bar(
            [xi + bar_width for xi in x],
            subset["seconds_bruteforce"],
            width=bar_width,
            label="brute force",
        )

        ax.set_title(f"Literals = {literals}")
        ax.set_ylabel("Time (seconds)")
        ax.set_xticks(list(x))
        ax.set_xticklabels(subset["clauses"].astype(str))
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend()

    axes[-1].set_xlabel("Number of clauses")
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=200)
        print(f"Saved plot to {output_path.resolve()}")
    else:
        plt.show()


def main() -> None:
    args = parse_args()

    df_eps01 = load_monte(args.eps01, label="eps01")
    df_eps005 = load_monte(args.eps005, label="eps005")
    df_bf = load_bruteforce(args.deterministic)

    merged = merge_available(df_bf, df_eps01, df_eps005)
    if merged.empty:
        raise SystemExit("No overlapping instances between brute force and Monte Carlo CSVs.")

    plot_bars(merged, args.output)


if __name__ == "__main__":
    main()
