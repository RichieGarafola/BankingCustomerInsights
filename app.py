"""Source-based Streamlit banking-marketing dashboard (no simulated live feed)."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import (
    deposit_by_job,
    filter_customers,
    summarize_customers,
    validate_customers,
)

st.set_page_config(
    page_title="Banking Customer Insights | Richie Garafola",
    page_icon="📊",
    layout="wide",
)
DATA_FILE = Path(__file__).resolve().parent / "Resources" / "Bank.csv"


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load the retained repository sample; do not fabricate live updates."""
    return validate_customers(pd.read_csv(DATA_FILE))


st.title("Banking Customer Insights")
st.markdown(
    "**Explore sample customer demographics, balances, and term-deposit "
    "subscription outcomes with auditable calculations.**"
)
st.info(
    "Historical sample analysis—not connected to a bank or live customer feed. "
    "Figures come directly from the included CSV; data provenance and licensing "
    "should be verified before reuse outside this demonstration."
)

try:
    all_customers = load_data()
except (OSError, pd.errors.ParserError, ValueError) as exc:
    st.error(f"Cannot load banking sample: {exc}")
    st.stop()

with st.sidebar:
    st.header("Filter sample records")
    all_jobs = sorted(all_customers["job"].unique().tolist())
    all_marital = sorted(all_customers["marital"].unique().tolist())
    jobs = st.multiselect("Job category", all_jobs, default=all_jobs)
    statuses = st.multiselect("Marital status", all_marital, default=all_marital)
    outcome = st.selectbox("Term deposit subscribed?", ["All", "Yes", "No"])
    minimum_age = int(all_customers["age"].min())
    maximum_age = int(all_customers["age"].max())
    ages = st.slider(
        "Age range",
        min_value=minimum_age,
        max_value=maximum_age,
        value=(minimum_age, maximum_age),
    )

subset = filter_customers(
    all_customers,
    jobs=jobs,
    marital=statuses,
    deposit=None if outcome == "All" else outcome.lower(),
    age_range=ages,
)
if subset.empty:
    st.warning("No sample records match these filters. Change the selection.")
    st.stop()

metrics = summarize_customers(subset)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Customers in sample", f"{metrics.customers:,}")
k2.metric("Average customer age", f"{metrics.average_age:.1f}")
k3.metric("Married customers", f"{metrics.married_customers:,}")
k4.metric("Average balance (source units)", f"{metrics.average_balance:,.2f}")

st.caption(
    f"Term-deposit subscribers: **{metrics.deposit_yes:,}** "
    f"({metrics.deposit_share:.1%} of selected sample). "
    "No random adjustments, deltas, or inferred trends are applied."
)

left, right = st.columns(2)
with left:
    age_chart = px.histogram(
        subset, x="age", nbins=25,
        title="Age distribution in selected sample",
        labels={"age": "Age", "count": "Records"},
    )
    age_chart.update_layout(yaxis_title="Records")
    st.plotly_chart(age_chart, use_container_width=True)
with right:
    balance_chart = px.histogram(
        subset, x="balance", nbins=35,
        title="Balance distribution in selected sample",
        labels={"balance": "Balance (source units)", "count": "Records"},
    )
    balance_chart.update_layout(yaxis_title="Records")
    st.plotly_chart(balance_chart, use_container_width=True)

st.subheader("Term-deposit subscription by job category")
breakdown = deposit_by_job(subset)
chart = px.bar(
    breakdown,
    x="job",
    y="share",
    hover_data=["customers", "yes"],
    title="Observed subscription share within each selected job category",
    labels={"job": "Job category", "share": "Share subscribed"},
)
chart.update_yaxes(tickformat=".0%", range=[0, 1])
st.plotly_chart(chart, use_container_width=True)
st.caption(
    "These are descriptive shares of selected sample records—not causal effects, "
    "bank-wide estimates, or forecasts. Small subgroups can be volatile."
)

with st.expander("Review source records and aggregate data"):
    fields = [c for c in ("age", "job", "marital", "education", "balance", "deposit") if c in subset]
    st.dataframe(subset[fields], use_container_width=True)
    st.dataframe(breakdown, use_container_width=True)
    st.download_button(
        "Download aggregate results (CSV)",
        breakdown.to_csv(index=False).encode("utf-8"),
        file_name="banking_job_subscription_summary.csv",
        mime="text/csv",
    )

st.caption(
    "The original version animated metrics by multiplying records by random factors "
    "and adding random counts. This version displays source-grounded, deterministic "
    "statistics and makes no real-time data claims."
)
