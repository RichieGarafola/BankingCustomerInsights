"""Headless app startup smoke test; the app performs no external requests."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_default_dashboard_renders_without_exceptions():
    script = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(script, default_timeout=45).run()
    assert len(app.exception) == 0
    assert app.title[0].value == "Banking Customer Insights"
    assert len(app.metric) == 4
