from __future__ import annotations

import streamlit as st

from config import DEFAULT_CONFIG
from data_gen.fake_data import build_default_forces
from data_gen.scenarios import DEFAULT_SCENARIOS
from decision_support.rules import ThreatPriorityPolicy
from persistence.replay import EventLog
from simulation.world import SimulationWorld
from ui.map_renderer import render_map
from ui.metrics_display import render_metrics


@st.cache_data(show_spinner=False)
def run_simulation(seed: int, min_threat_level_to_fire: int) -> tuple[list[dict], str]:
    bases, effectors, threats = build_default_forces(DEFAULT_CONFIG, seed=seed)
    policy = ThreatPriorityPolicy(min_threat_level=min_threat_level_to_fire)
    world = SimulationWorld(
        config=DEFAULT_CONFIG,
        policy=policy,
        bases=bases,
        effectors=effectors,
        threats=threats,
        seed=seed,
    )
    history, events, _metrics = world.run()
    log = EventLog()
    log.extend(events)
    return history, log.to_json()


def main() -> None:
    st.set_page_config(page_title="Air Defense Simulation Prototype", layout="wide")
    st.title("Air Defense Simulation Prototype")
    st.write(
        "Hackathon MVP: deterministic simulation, realistic synthetic threat waves, "
        "resource depletion/replenishment, and replay-driven map visualization."
    )

    scenario_names = [scenario.name for scenario in DEFAULT_SCENARIOS]
    selected_name = st.sidebar.selectbox("Scenario", scenario_names)
    selected_scenario = next(s for s in DEFAULT_SCENARIOS if s.name == selected_name)

    with st.sidebar:
        st.subheader("Run Controls")
        min_threat_level = st.slider(
            "Minimum Threat Level To Engage",
            min_value=1,
            max_value=10,
            value=selected_scenario.min_threat_level_to_fire,
        )
        seed = st.number_input("Seed", min_value=1, max_value=9999, value=selected_scenario.seed)

    history, replay_json = run_simulation(int(seed), int(min_threat_level))
    frame_index = st.slider("Timeline", min_value=0, max_value=len(history) - 1, value=0)
    snapshot = history[frame_index]

    left, right = st.columns([3, 2])
    with left:
        st.subheader(f"Operational Map - Tick {snapshot['tick']}")
        render_map(snapshot)

    with right:
        st.subheader("Evaluation Metrics")
        render_metrics(snapshot)
        st.download_button(
            label="Download Replay Log",
            data=replay_json,
            file_name=f"replay_{selected_name.lower()}_seed_{seed}.json",
            mime="application/json",
        )

        total_threats = len(snapshot["threats"])
        active_threats = len([item for item in snapshot["threats"] if item["alive"]])
        st.write(f"Total threats: {total_threats}")
        st.write(f"Active threats: {active_threats}")

        st.subheader("Effector Ammunition")
        for effector in snapshot["effectors"]:
            st.write(f"{effector['id']}: {effector['missiles']} missiles, cooldown {effector['cooldown']}")


if __name__ == "__main__":
    main()
