import argparse
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Plot samples used and runtime versus number of clauses "
            "for eps=0.1, delta=0.1 Monte Carlo runs."
        )
    )
    parser.add_argument(
        "--csv",
        default=None,
        type=Path,
        help="Path to the monte_summary CSV file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save the plot; if not given the plot is shown.",
    )
    return parser.parse_args()


def extract_metadata(file_col: pd.Series) -> pd.DataFrame:
    """Extract literals and clauses from the file column."""
    meta = file_col.str.extract(r"literals(?P<literals>\d+)_clauses(?P<clauses>\d+)")
    meta = meta.astype(int)
    return meta


def plot_metrics(df: pd.DataFrame, output_path: Optional[Path]) -> None:
    fig, (ax_samples, ax_time) = plt.subplots(1, 2, figsize=(12, 5), sharex=False)

    for literals, group in (
        df.sort_values("clauses").groupby("literals", sort=True)
    ):
        ax_samples.plot(
            group["clauses"],
            group["samples_used"],
            marker="o",
            label=f"literals={literals}",
        )
        ax_time.plot(
            group["clauses"],
            group["seconds"],
            marker="o",
            label=f"literals={literals}",
        )

    ax_samples.set_xlabel("Number of clauses")
    ax_samples.set_ylabel("Samples used")
    ax_samples.set_title("Samples vs. clauses (eps=0.1, delta=0.1)")
    ax_samples.grid(True, alpha=0.3)
    ax_samples.legend()

    ax_time.set_xlabel("Number of clauses")
    ax_time.set_ylabel("Time (seconds)")
    ax_time.set_title("Runtime vs. clauses (eps=0.1, delta=0.1)")
    ax_time.grid(True, alpha=0.3)
    ax_time.legend()

    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=200)
        print(f"Saved plot to {output_path.resolve()}")
    else:
        plt.show()


def main() -> None:
    args = parse_args()
    csv_path = (
        args.csv
        if args.csv
        else Path(__file__).resolve().parent / "monte_summary_all_eps0.1_delta0.1_latest.csv"
    )

    df = pd.read_csv(csv_path)
    df = df[df["status"] == "ok"].copy()
    meta = extract_metadata(df["file"])
    df = pd.concat([df, meta], axis=1)

    plot_metrics(df, args.output)


if __name__ == "__main__":
    main()
