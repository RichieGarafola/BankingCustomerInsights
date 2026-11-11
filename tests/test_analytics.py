"""Deterministic regression tests for customer-sample reporting."""

import pandas as pd
import pytest

from analytics import (
    deposit_by_job,
    filter_customers,
    summarize_customers,
    validate_customers,
)


@pytest.fixture
def customers():
    return validate_customers(
        pd.DataFrame(
            {
                "Unnamed: 0": [0, 1, 2, 3],
                "age": [30, 40, 50, 60],
                "job": ["Admin", "Admin", "Tech", "Tech"],
                "marital": ["married", "single", "married", "divorced"],
                "balance": [100, -50, 0, 150],
                "deposit": ["yes", "no", "yes", "no"],
            }
        )
    )


def test_normalization_preserves_raw_values_and_removes_csv_index(customers):
    assert "Unnamed: 0" not in customers.columns
    assert customers["job"].tolist() == ["admin", "admin", "tech", "tech"]
    assert customers["balance"].tolist() == [100, -50, 0, 150]


def test_metrics_are_exact_counts_not_simulated(customers):
    first = summarize_customers(customers)
    second = summarize_customers(customers)
    assert first == second
    assert first.customers == 4
    assert first.average_age == pytest.approx(45)
    assert first.married_customers == 2
    assert first.average_balance == pytest.approx(50)
    assert first.deposit_yes == 2
    assert first.deposit_share == pytest.approx(0.5)


def test_filtering_does_not_change_source_records(customers):
    before = customers.copy(deep=True)
    selected = filter_customers(
        customers, jobs=["admin"], marital=["married"],
        deposit="yes", age_range=(18, 50)
    )
    assert len(selected) == 1
    assert selected.iloc[0]["balance"] == 100
    pd.testing.assert_frame_equal(customers, before)


def test_job_summary_counts_and_denominators(customers):
    summary = deposit_by_job(customers).set_index("job")
    assert summary.loc["admin", "customers"] == 2
    assert summary.loc["admin", "yes"] == 1
    assert summary.loc["admin", "share"] == pytest.approx(0.5)
    assert summary.loc["tech", "share"] == pytest.approx(0.5)


@pytest.mark.parametrize(
    "changes,match",
    [
        ({"age": [30, 0, 50, 60]}, "Age must"),
        ({"balance": [100, "bad", 0, 150]}, "balance has invalid"),
        ({"deposit": ["yes", "maybe", "no", "yes"]}, "Deposit outcome"),
        ({"job": ["admin", "", "tech", "tech"]}, "blank categories"),
    ],
)
def test_invalid_input_is_rejected(customers, changes, match):
    raw = customers.copy()
    for field, values in changes.items():
        raw[field] = values
    with pytest.raises(ValueError, match=match):
        validate_customers(raw)


def test_missing_column_rejected(customers):
    with pytest.raises(ValueError, match="Missing columns"):
        validate_customers(customers.drop(columns=["balance"]))


def test_empty_selection_does_not_fabricate_kpis(customers):
    filtered = filter_customers(customers, jobs=["not-a-real-job"])
    with pytest.raises(ValueError, match="No records"):
        summarize_customers(filtered)


def test_invalid_deposit_filter_rejected(customers):
    with pytest.raises(ValueError, match="yes or no"):
        filter_customers(customers, deposit="maybe")
