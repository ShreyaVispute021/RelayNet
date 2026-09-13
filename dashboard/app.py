from pathlib import Path
import subprocess
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

SCENARIO_LABELS = {
    "normal": "Normal",
    "high_mobility": "High Mobility",
    "high_congestion": "High Congestion",
    "low_battery": "Low Battery",
    "relay_failure": "Relay Failure",
}

METHOD_LABELS = {
    "static": "Static",
    "baseline": "Weighted Baseline",
    "contextual_kg": "Contextual KG",
    "kg_marl": "KG + MARL",
}

MODULES = {
    "MANET topology": "python.experiments.manet_simulation",
    "Knowledge Graph": "python.relaynet.knowledge_graph",
    "KG visualization": "python.experiments.visualize_knowledge_graph",
    "KG + MARL training": "python.experiments.kg_marl_experiment",
    "Multi-seed evaluation": "python.experiments.multi_seed_evaluation",
}


st.set_page_config(
    page_title="RelayNet Control Center",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --cyan: #22d3ee; --blue: #2563eb; --panel: #101827; }
    .stApp { background: linear-gradient(145deg, #07101e 0%, #0b1220 58%, #101b2f 100%); }
    [data-testid="stSidebar"] { background: #080f1c; border-right: 1px solid #1f334d; }
    [data-testid="stMetric"] {
        background: linear-gradient(150deg, rgba(19,31,51,.96), rgba(12,23,40,.96));
        border: 1px solid #223a59; border-radius: 14px; padding: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,.18);
    }
    [data-testid="stMetricValue"] { color: #e7f7ff; }
    [data-testid="stMetricLabel"] { color: #9fb8cf; }
    .relay-title { font-size: 2.15rem; font-weight: 760; color: #f4fbff; margin-bottom: .1rem; }
    .relay-subtitle { color: #8eaac2; font-size: 1rem; margin-bottom: 1.2rem; }
    .status-strip {
        border: 1px solid #1e4960; background: rgba(12,39,55,.72); color: #c8f5ff;
        border-radius: 12px; padding: .72rem 1rem; margin: .25rem 0 1rem;
    }
    .section-note { color: #91a8bf; font-size: .94rem; }
    .stTabs [data-baseweb="tab-list"] { gap: .45rem; }
    .stTabs [data-baseweb="tab"] {
        background: #101b2b; border: 1px solid #203650; border-radius: 10px;
        padding: .45rem .9rem;
    }
    .stTabs [aria-selected="true"] { background: #12344c; border-color: #22d3ee; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_csv(filename):
    path = RESULTS_DIR / filename
    if not path.exists():
        return None
    return pd.read_csv(path)


def show_image(filename, caption):
    path = RESULTS_DIR / filename
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.warning(f"Generate `{filename}` from the Simulation Lab tab.")


def run_module(module):
    process = subprocess.run(
        [sys.executable, "-m", module],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    return process.returncode, process.stdout, process.stderr


summary = load_csv("multi_seed_summary.csv")

st.sidebar.markdown("## RelayNet")
st.sidebar.caption("AEMRP research prototype")
scenario = st.sidebar.selectbox(
    "Disaster scenario",
    list(SCENARIO_LABELS),
    format_func=SCENARIO_LABELS.get,
)
selected_method = st.sidebar.selectbox(
    "Routing method",
    list(METHOD_LABELS),
    index=3,
    format_func=METHOD_LABELS.get,
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Network model**")
st.sidebar.caption("1 source · 1 destination · 3 UAV relays")
st.sidebar.markdown("**Evaluation design**")
st.sidebar.caption("5 scenarios · 4 methods · 10 seeds")
st.sidebar.markdown("**Intelligence layer**")
st.sidebar.caption("Temporal KG + independent Q-learning")

st.markdown('<div class="relay-title">RelayNet Control Center</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="relay-subtitle">Infrastructure-less disaster MANET monitoring, reasoning and evaluation</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="status-strip">● Simulation prototype operational &nbsp; · &nbsp; '
    'MANET routing &nbsp; · &nbsp; Temporal KG &nbsp; · &nbsp; Multi-agent learning</div>',
    unsafe_allow_html=True,
)

if summary is None:
    st.error("Multi-seed results are missing. Run the evaluation from Simulation Lab.")
else:
    selected_rows = summary[
        (summary["scenario"] == scenario)
        & (summary["selection_method"] == selected_method)
    ]
    if selected_rows.empty:
        st.error("The selected scenario and method are not present in the results.")
    else:
        row = selected_rows.iloc[0]
        metric_columns = st.columns(6)
        metrics = (
            ("PDR", f"{row['pdr_mean']:.2%}", f"±{row['pdr_std']:.2%}"),
            ("Packet loss", f"{row['loss_ratio_mean']:.2%}", None),
            ("Average delay", f"{row['average_delay_mean']:.2f}", "steps"),
            ("Throughput", f"{row['throughput_kbps_mean']:.3f}", "kbps"),
            ("Energy used", f"{row['energy_consumed_mean']:.1f}", "units"),
            ("Lifetime", f"{row['network_lifetime_steps_mean']:.0f}", "steps"),
        )
        for column, (label, value, delta) in zip(metric_columns, metrics):
            column.metric(label, value, delta)

tabs = st.tabs([
    "Overview",
    "MANET",
    "Knowledge Graph",
    "Q-Learning",
    "Performance",
    "Simulation Lab",
])

with tabs[0]:
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.subheader(f"{SCENARIO_LABELS[scenario]} comparison")
        if summary is not None:
            comparison = summary[summary["scenario"] == scenario].copy()
            comparison["Method"] = comparison["selection_method"].map(METHOD_LABELS)
            comparison["PDR (%)"] = comparison["pdr_mean"] * 100
            comparison["Loss (%)"] = comparison["loss_ratio_mean"] * 100
            comparison = comparison.rename(
                columns={
                    "average_delay_mean": "Delay",
                    "throughput_kbps_mean": "Throughput (kbps)",
                    "energy_consumed_mean": "Energy",
                    "network_lifetime_steps_mean": "Lifetime",
                }
            )
            st.dataframe(
                comparison[["Method", "PDR (%)", "Loss (%)", "Delay", "Throughput (kbps)", "Energy", "Lifetime"]],
                hide_index=True,
                use_container_width=True,
            )
            chart_data = comparison.set_index("Method")[["PDR (%)"]]
            st.bar_chart(chart_data, color="#22d3ee")
    with right:
        st.subheader("Decision pipeline")
        st.markdown(
            """
            1. UAV relays advertise their current network state.
            2. MANET neighbour discovery creates feasible wireless links.
            3. The temporal KG derives context and safety recommendations.
            4. Each relay retrieves its learned Q-value for the current state.
            5. AERA combines context and experience to select a relay.
            6. Delivery feedback updates performance and learning metrics.
            """
        )
        st.info(
            "KG + MARL is strongest under high mobility in the present evaluation. "
            "Low-battery reward shaping remains the main optimization target."
        )

with tabs[1]:
    st.subheader("Dynamic MANET topology")
    st.markdown(
        '<p class="section-note">Solid red edges show the discovered route; dashed edges are available wireless links.</p>',
        unsafe_allow_html=True,
    )
    show_image("manet_topology.png", "Topology evolution at T0, T5 and T10")
    routing_log = load_csv("manet_routing_log.csv")
    if routing_log is not None:
        st.dataframe(routing_log, hide_index=True, use_container_width=True)

with tabs[2]:
    st.subheader("Temporal Knowledge Graph reasoning")
    show_image(
        "kg_simulation_graph.png",
        "Relay context and recommendations at T0, T5 and T10",
    )
    kg = load_csv("relaynet_knowledge_graph.csv")
    if kg is not None:
        predicate = st.selectbox(
            "Inspect KG relation",
            sorted(kg["predicate"].unique()),
            index=0,
        )
        st.dataframe(
            kg[kg["predicate"] == predicate].head(50),
            hide_index=True,
            use_container_width=True,
        )

with tabs[3]:
    st.subheader("Independent Q-learning agents")
    parameter_data = None
    parameter_path = RESULTS_DIR / "rl_parameters.json"
    if parameter_path.exists():
        parameter_data = pd.read_json(parameter_path, typ="series")

    left, right = st.columns([0.75, 1.5], gap="large")
    with left:
        st.markdown("#### Hyperparameters")
        if parameter_data is not None:
            parameters = parameter_data.rename_axis("Parameter").reset_index(name="Value")
            st.dataframe(parameters, hide_index=True, use_container_width=True)
        else:
            st.warning("RL parameter export is not available.")
        st.latex(r"Q(s,a) \leftarrow Q(s,a) + \alpha[r + \gamma Q(s',a) - Q(s,a)]")
        st.latex(r"Score = 0.65\,KG + 0.35\,Q")
    with right:
        show_image("rl_training_progress.png", "Reward, delivery rate, TD error and exploration")

    q_tables = load_csv("marl_q_tables.csv")
    if q_tables is not None:
        st.markdown(f"#### Learned Q-table · {len(q_tables)} entries")
        relay_filter = st.multiselect(
            "Relay agents",
            sorted(q_tables["relay_id"].unique()),
            default=sorted(q_tables["relay_id"].unique()),
        )
        st.dataframe(
            q_tables[q_tables["relay_id"].isin(relay_filter)],
            hide_index=True,
            use_container_width=True,
        )

with tabs[4]:
    st.subheader("Ten-seed performance evaluation")
    metric_images = {
        "Packet Delivery Ratio": "multi_seed_pdr.png",
        "Packet Loss": "multi_seed_loss_ratio.png",
        "Average Delay": "multi_seed_average_delay.png",
        "Throughput": "multi_seed_throughput_kbps.png",
        "Energy Consumption": "multi_seed_energy_consumed.png",
        "Network Lifetime": "multi_seed_network_lifetime_steps.png",
    }
    selected_chart = st.selectbox("Evaluation metric", list(metric_images))
    show_image(metric_images[selected_chart], selected_chart)
    if summary is not None:
        st.download_button(
            "Download summary CSV",
            summary.to_csv(index=False),
            file_name="relaynet_multi_seed_summary.csv",
            mime="text/csv",
        )

with tabs[5]:
    st.subheader("Run verified experiments")
    st.caption("Run one module at a time. Longer evaluations may take several seconds.")
    module_label = st.selectbox("Experiment", list(MODULES))
    if st.button("Run experiment", type="primary", use_container_width=True):
        with st.spinner(f"Running {module_label}..."):
            try:
                code, stdout, stderr = run_module(MODULES[module_label])
            except subprocess.TimeoutExpired:
                st.error("The experiment exceeded the 180-second dashboard limit.")
            else:
                if code == 0:
                    st.success(f"{module_label} completed successfully.")
                    st.cache_data.clear()
                else:
                    st.error(f"{module_label} exited with code {code}.")
                st.code(stdout or stderr or "No terminal output", language="text")
                if stderr and stdout:
                    with st.expander("Diagnostic output"):
                        st.code(stderr, language="text")

