"""Validated, deterministic statistics for the banking marketing sample.

This module never fabricates customer-level attributes or changes KPI counts.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ("age", "job", "marital", "balance", "deposit")


@dataclass(frozen=True)
class CustomerMetrics:
    customers: int
    average_age: float
    married_customers: int
    average_balance: float
    deposit_yes: int
    deposit_share: float


def validate_customers(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate the supplied dataset and normalize key categorical fields."""
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ValueError("An input table with customer records is required.")
    if frame.columns.has_duplicates:
        raise ValueError("Duplicate column names are not supported.")
    missing = [name for name in REQUIRED_COLUMNS if name not in frame]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    clean = frame.copy()

    for col in ("age", "balance"):
        numeric = pd.to_numeric(clean[col], errors="coerce")
        if numeric.isna().any() or not np.isfinite(numeric.to_numpy()).all():
            raise ValueError(f"{col} has invalid or missing numeric data.")
        clean[col] = numeric

    if ((clean["age"] <= 0) | (clean["age"] > 120)).any():
        raise ValueError("Age must be between 1 and 120.")

    for col in ("job", "marital", "deposit"):
        if clean[col].isna().any():
            raise ValueError(f"{col} includes missing categories.")
        clean[col] = clean[col].astype(str).str.strip().str.lower()
        if clean[col].eq("").any():
            raise ValueError(f"{col} includes blank categories.")

    if not clean["deposit"].isin(("yes", "no")).all():
        raise ValueError("Deposit outcome must be yes or no.")

    # A CSV row number is not a reliable customer identifier.
    clean = clean.loc[:, ~clean.columns.astype(str).str.startswith("Unnamed:")]
    return clean


def filter_customers(
    frame: pd.DataFrame,
    *,
    jobs: list[str] | None = None,
    marital: list[str] | None = None,
    deposit: str | None = None,
    age_range: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """Apply transparent filters to an already validated data table."""
    selected = frame
    if jobs is not None:
        selected = selected[selected["job"].isin(jobs)]
    if marital is not None:
        selected = selected[selected["marital"].isin(marital)]
    if deposit is not None:
        if deposit not in ("yes", "no"):
            raise ValueError("Deposit filter must be yes or no.")
        selected = selected[selected["deposit"] == deposit]
    if age_range is not None:
        lower, upper = age_range
        if lower > upper:
            raise ValueError("Invalid age range.")
        selected = selected[selected["age"].between(lower, upper)]
    return selected.copy()


def summarize_customers(frame: pd.DataFrame) -> CustomerMetrics:
    """Calculate actual sample statistics; never add random offsets."""
    if frame.empty:
        raise ValueError("No records match the selected filters.")
    n = len(frame)
    yes = int(frame["deposit"].eq("yes").sum())
    return CustomerMetrics(
        customers=n,
        average_age=float(frame["age"].mean()),
        married_customers=int(frame["marital"].eq("married").sum()),
        average_balance=float(frame["balance"].mean()),
        deposit_yes=yes,
        deposit_share=yes / n,
    )


def deposit_by_job(frame: pd.DataFrame) -> pd.DataFrame:
    """Group-level term-deposit subscription counts and observed shares."""
    if frame.empty:
        return pd.DataFrame(columns=["job", "customers", "yes", "share"])
    summary = (
        frame.groupby("job", dropna=False)
        .agg(customers=("deposit", "size"), yes=("deposit", lambda x: x.eq("yes").sum()))
        .reset_index()
    )
    summary["share"] = summary["yes"] / summary["customers"]
    return summary.sort_values("customers", ascending=False).reset_index(drop=True)
