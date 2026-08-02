import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy Dashboard",
    page_icon="🍬",
    layout="wide"
)

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/raw/Nassau Candy Distributor.csv")

    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        errors="coerce"
    )

    df["Ship Date"] = pd.to_datetime(
        df["Ship Date"],
        errors="coerce"
    )

    return df

df = load_data()

# --------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------
st.sidebar.title("Dashboard Filters")

# Division Filter
division = st.sidebar.selectbox(
    "Select Division",
    ["All"] + sorted(df["Division"].dropna().unique())
)

# Date Filter
start_date = st.sidebar.date_input(
    "Start Date",
    value=df["Order Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=df["Order Date"].max()
)

# Product Search
search_product = st.sidebar.text_input(
    "Search Product"
)

# --------------------------------------------------------
# FILTER DATA
# --------------------------------------------------------

filtered_df = df.copy()

# Division Filter
if division != "All":
    filtered_df = filtered_df[
        filtered_df["Division"] == division
    ]

# Date Filter
filtered_df = filtered_df[
    (filtered_df["Order Date"] >= pd.to_datetime(start_date))
    &
    (filtered_df["Order Date"] <= pd.to_datetime(end_date))
]

# Product Search
if search_product != "":
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(search_product,
                      case=False,
                      na=False)
    ]

# --------------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------------

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Gross Profit"].sum()

total_units = filtered_df["Units"].sum()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

# --------------------------------------------------------
# TITLE
# --------------------------------------------------------

st.title("🍬 Product Line Profitability & Margin Performance Analysis")

st.markdown("### Nassau Candy Distributor")

# --------------------------------------------------------
# KPI CARDS
# --------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Sales",
    f"${total_sales:,.2f}"
)

col2.metric(
    "📈 Gross Profit",
    f"${total_profit:,.2f}"
)

col3.metric(
    "📦 Units Sold",
    f"{int(total_units):,}"
)

col4.metric(
    "📊 Profit Margin",
    f"{profit_margin:.2f}%"
)

st.divider()

# --------------------------------------------------------
# DATASET PREVIEW
# --------------------------------------------------------

st.subheader("Dataset Preview")

st.dataframe(filtered_df)