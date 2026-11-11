"""Headless app startup smoke test; the app performs no external requests."""

from streamlit.testing.v1 import AppTest


def test_default_dashboard_renders_without_exceptions():
    app = AppTest.from_file("app.py", default_timeout=45).run()
    assert len(app.exception) == 0
    assert app.title[0].value == "Banking Customer Insights"
    assert len(app.metric) == 4
