from __future__ import annotations

import pandas as pd
import streamlit as st


def render_map(snapshot: dict) -> None:
    base_rows = [
        {
            "lat": item["lat"],
            "lon": item["lon"],
            "label": f"BASE: {item['name']}",
            "kind": "base",
            "size": 140,
        }
        for item in snapshot["bases"]
    ]
    alive_threat_rows = [
        {
            "lat": item["lat"],
            "lon": item["lon"],
            "label": f"THREAT {item['id']} (L{item['threat_level']})",
            "kind": "threat",
            "size": 90,
        }
        for item in snapshot["threats"]
        if item["alive"]
    ]

    data = pd.DataFrame(base_rows + alive_threat_rows)
    if data.empty:
        st.info("No active map entities in this frame.")
        return

    st.map(data, latitude="lat", longitude="lon", size="size")
    st.caption("Blue markers indicate bases. Red markers indicate active threats.")
