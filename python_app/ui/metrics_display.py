from __future__ import annotations

import streamlit as st


def render_metrics(snapshot: dict) -> None:
    metrics = snapshot["metrics"]
    c1, c2 = st.columns(2)
    c1.metric("Intercept Rate", f"{metrics['intercept_rate'] * 100:.1f}%")
    c2.metric("Score", f"{metrics['score']:.2f}")

    c3, c4 = st.columns(2)
    c3.metric("Missiles Fired", f"{int(metrics['missiles_fired'])}")
    c4.metric("Missiles / Intercept", f"{metrics['missiles_per_intercept']:.2f}")

    c5, c6 = st.columns(2)
    c5.metric("Threats Intercepted", f"{int(metrics['threats_intercepted'])}")
    c6.metric("Threats Escaped", f"{int(metrics['threats_escaped'])}")
