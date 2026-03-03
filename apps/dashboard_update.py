from core.data import generator as DG
import streamlit as st
import pandas as pd

from core.duplicates.user_defined_merge_data_update import display_merge_data
from sections import value_distribution as vdm
from sections import duplicates as dm
from sections import nulls as nm
from sections import cardinality as cm
from sections import outliers as om
from sections import score as ScM
from sections import consistency as ConM

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="DQ Agent - Data Quality Platform",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
        :root {
            --bg-top: #edf4f8;
            --bg-bottom: #f7fafc;
            --surface: #ffffff;
            --surface-alt: #f6f9fb;
            --border: #d7e1e8;
            --text-strong: #13293d;
            --text-muted: #516477;
            --brand: #1f5a7a;
            --brand-soft: #2d7aa0;
            --accent: #0f8b8d;
        }

        .stApp {
            background:
                radial-gradient(1200px 500px at 0% -10%, #e7f1f7 0%, transparent 60%),
                linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
            color: var(--text-strong);
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(1200px 500px at 0% -10%, #e7f1f7 0%, transparent 60%),
                linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
        }

        html, body, [class*="css"] {
            font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }

        .main .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 100%;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f2f45 0%, #174966 100%);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem;
        }

        [data-testid="stSidebar"] * {
            color: #eef5fb !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(234, 243, 251, 0.2);
        }

        [data-testid="stSidebar"] .stButton > button {
            border: 1px solid rgba(222, 236, 247, 0.28);
            background: rgba(255, 255, 255, 0.06);
            color: #f5fbff;
            border-radius: 10px;
            font-weight: 600;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: rgba(255, 255, 255, 0.55);
            background: rgba(255, 255, 255, 0.12);
        }

        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-baseweb="textarea"] > div {
            background: #ffffff;
            border-color: var(--border);
            color: var(--text-strong);
        }

        [data-baseweb="tab-list"] button {
            background: #edf4f8;
            color: var(--text-strong);
            border-radius: 8px;
        }

        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
        }

        [data-testid="stDataFrame"] [role="columnheader"] {
            background: #edf4f8;
            color: var(--text-strong);
        }

        [data-testid="stDataFrame"] [role="gridcell"] {
            background: #ffffff;
            color: var(--text-strong);
        }

        .hero-shell {
            border: 1px solid var(--border);
            background: linear-gradient(135deg, #ffffff 0%, #f2f8fc 60%, #eef4f8 100%);
            border-radius: 16px;
            padding: 2.3rem 2rem;
            box-shadow: 0 10px 30px rgba(20, 52, 75, 0.07);
            margin-bottom: 1.4rem;
        }

        .hero-kicker {
            display: inline-block;
            font-size: 0.78rem;
            letter-spacing: 0.55px;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--brand);
            background: #eaf3f9;
            border: 1px solid #cfe2ee;
            border-radius: 999px;
            padding: 0.28rem 0.7rem;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: 2.5rem;
            line-height: 1.18;
            margin: 0;
            color: var(--text-strong);
            font-weight: 750;
        }

        .hero-subtitle {
            margin-top: 0.8rem;
            color: var(--text-muted);
            font-size: 1.08rem;
            max-width: 760px;
        }

        .feature-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.5rem 1.2rem;
            min-height: 180px;
            box-shadow: 0 4px 12px rgba(20, 52, 75, 0.05);
        }

        .feature-title {
            color: var(--text-strong);
            margin: 0;
            font-size: 1.02rem;
            font-weight: 700;
        }

        .feature-copy {
            color: var(--text-muted);
            margin-top: 0.6rem;
            line-height: 1.45;
            font-size: 0.95rem;
        }

        .feature-tag {
            color: var(--brand-soft);
            font-weight: 700;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 12px;
            border-radius: 12px;
        }

        .stAlert {
            border-radius: 10px;
            border: 1px solid var(--border);
        }

        .dataframe {
            font-size: 0.9rem;
            border: 1px solid var(--border);
            border-radius: 12px;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'df' not in st.session_state:
    st.session_state.df = None
if 'dataset_ready' not in st.session_state:
    st.session_state.dataset_ready = False
if 'dataset_label' not in st.session_state:
    st.session_state.dataset_label = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Data Preview"
if 'selected_cols' not in st.session_state:
    st.session_state.selected_cols = []

# ==================== CACHED LOADERS ====================
@st.cache_data(show_spinner="Loading CSV file...")
def load_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

@st.cache_data(show_spinner="Loading Excel file...")
def load_excel(file) -> pd.DataFrame:
    return pd.read_excel(file)

@st.cache_data(show_spinner="Generating synthetic data...")
def generate_data(n_rows: int) -> pd.DataFrame:
    return DG.get_data(n_rows)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## DQ Agent")
    st.caption("Enterprise Data Quality Platform")
    st.divider()

    # ==================== DATA SOURCE SECTION ====================
    st.markdown("### Data Source")

    data_source = st.radio(
        "Select source:",
        ["Upload File", "Generate Data"],
        label_visibility="collapsed"
    )

    uploaded_file = None
    n_rows = None

    if data_source == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel",
            type=["csv", "xlsx", "xls"],
            help="Maximum file size: 200MB"
        )
    else:
        n_rows = st.number_input(
            "Number of rows",
            min_value=100,
            max_value=200000,
            value=20000,
            step=1000,
            help="Generate synthetic data for testing"
        )

    load_button = st.button("Load Dataset", type="primary", use_container_width=True)

    # Load dataset
    if load_button:
        try:
            with st.spinner("Loading data..."):
                if data_source == "Upload File":
                    if uploaded_file is None:
                        st.error("Please upload a file first.")
                        st.session_state.dataset_ready = False
                    else:
                        name = uploaded_file.name.lower()
                        if name.endswith(".csv"):
                            df = load_csv(uploaded_file)
                        else:
                            df = load_excel(uploaded_file)

                        st.session_state.df = df
                        st.session_state.dataset_ready = True
                        st.session_state.dataset_label = uploaded_file.name
                        st.session_state.selected_cols = df.columns.tolist()
                        st.success(f"Loaded: {uploaded_file.name}")
                        st.rerun()
                else:
                    df = generate_data(int(n_rows))
                    st.session_state.df = df
                    st.session_state.dataset_ready = True
                    st.session_state.dataset_label = f"Generated Dataset ({int(n_rows):,} rows)"
                    st.session_state.selected_cols = df.columns.tolist()
                    st.success(f"Generated {int(n_rows):,} rows")
                    st.rerun()

        except Exception as e:
            st.session_state.dataset_ready = False
            st.session_state.df = None
            st.error(f"Error: {str(e)}")

    # Dataset info
    if st.session_state.dataset_ready and st.session_state.df is not None:
        st.divider()
        st.markdown("### Dataset Info")

        df = st.session_state.df

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", len(df.columns))

        st.caption(f"**Source:** {st.session_state.dataset_label}")

        # Column filter
        st.divider()
        st.markdown("### Column Filter")

        filter_enabled = st.checkbox("Filter columns", value=False)

        if filter_enabled:
            selected_cols = st.multiselect(
                "Select columns:",
                df.columns.tolist(),
                default=st.session_state.selected_cols,
                label_visibility="collapsed"
            )
            st.session_state.selected_cols = selected_cols if selected_cols else df.columns.tolist()
        else:
            st.session_state.selected_cols = df.columns.tolist()

        # Navigation
        st.divider()
        st.markdown("### Navigation")

        pages = {
            "Data Preview": "Data Preview",
            "Quality Score": "Score",
            "Distribution": "Distribution",
            "Cardinality": "Cardinality",
            "Duplicates": "Duplicates",
            "Nulls": "Nulls",
            "Outliers": "Outliers",
            "Consistency": "Consistency",
            "Data Merger": "Merger"
        }

        for label, page_id in pages.items():
            if st.button(
                label,
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_id else "secondary"
            ):
                st.session_state.current_page = page_id
                st.rerun()

        st.divider()

        # Clear dataset
        if st.button("Clear Dataset", use_container_width=True):
            st.session_state.df = None
            st.session_state.dataset_ready = False
            st.session_state.dataset_label = ""
            st.session_state.current_page = "Data Preview"
            st.rerun()

# ==================== MAIN CONTENT ====================

# If no dataset, show welcome screen
if not st.session_state.dataset_ready or st.session_state.df is None:
    st.markdown("""
        <div class='hero-shell'>
            <span class='hero-kicker'>Data Reliability Workspace</span>
            <h1 class='hero-title'>Operational Data Quality for Business Teams</h1>
            <p class='hero-subtitle'>
                Audit completeness, duplication, cardinality, outliers, and rule consistency from one governed interface.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Feature showcase
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-tag'>Profiling</div>
                <h3 class='feature-title'>Comprehensive Data Scans</h3>
                <p class='feature-copy'>Evaluate core quality dimensions across high-volume datasets with fast previews and metrics.</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-tag'>Scoring</div>
                <h3 class='feature-title'>Executive Quality KPIs</h3>
                <p class='feature-copy'>Track health indicators and expose risk areas that impact downstream reporting and automation.</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class='feature-card'>
                <div class='feature-tag'>Resolution</div>
                <h3 class='feature-title'>Guided Record Merging</h3>
                <p class='feature-copy'>Resolve duplicates with weighted matching logic and controlled review workflows.</p>
            </div>
        """, unsafe_allow_html=True)

    st.stop()

# ==================== PAGE ROUTING ====================
df = st.session_state.df
filtered_df = df[st.session_state.selected_cols] if st.session_state.selected_cols else df

current_page = st.session_state.current_page

# Page header
st.markdown(f"<h1 style='margin-bottom: 0;'>{current_page}</h1>", unsafe_allow_html=True)
st.caption(f"Dataset: {st.session_state.dataset_label} | {len(df):,} rows x {len(filtered_df.columns)} columns")
st.divider()

# Route to appropriate page
if current_page == "Data Preview":
    st.dataframe(
        filtered_df.head(10000),
        use_container_width=True,
        height=600
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        st.metric("Displayed Columns", len(filtered_df.columns))
    with col4:
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("Memory Usage", f"{memory_mb:.2f} MB")

elif current_page == "Score":
    ScM.displayScoreStats(filtered_df)

elif current_page == "Distribution":
    vdm.displayValueDistributionStats(filtered_df)

elif current_page == "Cardinality":
    cm.displayCardinalityStats(filtered_df)

elif current_page == "Duplicates":
    dm.displayDuplicateStats(filtered_df)

elif current_page == "Nulls":
    nm.displayNullStats(filtered_df)

elif current_page == "Outliers":
    om.displayOutlierStats(filtered_df)

elif current_page == "Consistency":
    ConM.displayConsistencyStats(filtered_df)

elif current_page == "Merger":
    st.warning("BETA feature: Data Merger uses weighted scoring. Back up your data before merging.")
    st.info("Tip: This feature performs best with datasets under 5,000 rows.")
    display_merge_data(filtered_df)

# ==================== FOOTER ====================
st.divider()
st.markdown("""
    <div style='text-align: center; color: #6b7280; padding: 1rem;'>
        <p style='margin: 0;'>DQ Agent v2.0 | Built with Streamlit | 2024</p>
    </div>
""", unsafe_allow_html=True)
