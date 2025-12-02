import math
from pathlib import Path


def load_numbers(path):
    with open(path, "r") as f:
        return [float(line.strip()) for line in f if line.strip()]


def main():
    base = Path("Data")
    file_a = base / "samples1000_literals20_clauses-1_var_width1_sol.txt"
    file_b = base / "samples1000_literals20_clauses-1_var_width1_output.txt"

    a_vals = load_numbers(file_a)
    b_vals = load_numbers(file_b)

    if len(a_vals) != len(b_vals):
        raise ValueError(f"Length mismatch: {len(a_vals)} vs {len(b_vals)}")

    mae = sum(abs(x - y) for x, y in zip(a_vals, b_vals)) / len(a_vals) if a_vals else math.nan
    print(f"MAE: {mae}")


if __name__ == "__main__":
    main()
