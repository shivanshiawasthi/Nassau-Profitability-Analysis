import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy Dashboard",
    page_icon="🍬",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/raw/Nassau Candy Distributor.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")
    return df

df = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.title("Dashboard Filters")

division = st.sidebar.selectbox(
    "Select Division",
    ["All"] + sorted(df["Division"].dropna().unique())
)

start_date = st.sidebar.date_input(
    "Start Date",
    value=df["Order Date"].min().date()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=df["Order Date"].max().date()
)

product_search = st.sidebar.text_input("Search Product")

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
filtered_df = df.copy()

if division != "All":
    filtered_df = filtered_df[filtered_df["Division"] == division]

filtered_df = filtered_df[
    (filtered_df["Order Date"] >= pd.to_datetime(start_date))
    &
    (filtered_df["Order Date"] <= pd.to_datetime(end_date))
]

if product_search != "":
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(product_search, case=False, na=False)
    ]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0
    else 0
)

# --------------------------------------------------
# DASHBOARD TITLE
# --------------------------------------------------
st.title("🍬 Product Line Profitability & Margin Performance Analysis")
st.markdown("### Nassau Candy Distributor Dashboard")
st.divider()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"${total_sales:,.2f}")
col2.metric("📈 Gross Profit", f"${total_profit:,.2f}")
col3.metric("📦 Units Sold", f"{int(total_units):,}")
col4.metric("📊 Profit Margin", f"{profit_margin:.2f}%")

st.divider()

# --------------------------------------------------
# ROW 1 CHARTS
# --------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Sales by Division")

    sales_division = (
        filtered_df.groupby("Division", as_index=False)["Sales"]
        .sum()
    )

    fig_sales = px.bar(
        sales_division,
        x="Division",
        y="Sales",
        color="Division",
        text_auto=".2s"
    )

    fig_sales.update_layout(height=450)

    st.plotly_chart(fig_sales, use_container_width=True)

with col_right:
    st.subheader("🥧 Profit by Region")

    profit_region = (
        filtered_df.groupby("Region", as_index=False)["Gross Profit"]
        .sum()
    )

    fig_region = px.pie(
        profit_region,
        names="Region",
        values="Gross Profit",
        hole=0.45
    )

    fig_region.update_layout(height=450)

    st.plotly_chart(fig_region, use_container_width=True)

st.divider()

# --------------------------------------------------
# MONTHLY SALES TREND
# --------------------------------------------------
st.subheader("📈 Monthly Sales Trend")

filtered_df["Month Number"] = filtered_df["Order Date"].dt.month
filtered_df["Month"] = filtered_df["Order Date"].dt.strftime("%b")

monthly_sales = (
    filtered_df.groupby(["Month Number", "Month"], as_index=False)["Sales"]
    .sum()
    .sort_values("Month Number")
)

fig_month = px.line(
    monthly_sales,
    x="Month",
    y="Sales",
    markers=True,
    category_orders={
        "Month": [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]
    }
)

fig_month.update_layout(height=450)

st.plotly_chart(fig_month, use_container_width=True)

st.divider()

# --------------------------------------------------
# TOP 10 PRODUCTS BY SALES
# --------------------------------------------------
st.subheader("🏆 Top 10 Products by Sales")

top_sales = (
    filtered_df.groupby("Product Name", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
    .head(10)
)

fig_top_sales = px.bar(
    top_sales,
    x="Sales",
    y="Product Name",
    orientation="h",
    color="Sales",
    color_continuous_scale="Blues"
)

fig_top_sales.update_layout(
    yaxis=dict(categoryorder="total ascending"),
    height=500
)

st.plotly_chart(fig_top_sales, use_container_width=True)

st.divider()

# --------------------------------------------------
# TOP 10 PRODUCTS BY GROSS PROFIT
# --------------------------------------------------
st.subheader("💎 Top 10 Products by Gross Profit")

top_profit = (
    filtered_df.groupby("Product Name", as_index=False)["Gross Profit"]
    .sum()
    .sort_values("Gross Profit", ascending=False)
    .head(10)
)

fig_profit = px.bar(
    top_profit,
    x="Gross Profit",
    y="Product Name",
    orientation="h",
    color="Gross Profit",
    color_continuous_scale="Greens"
)

fig_profit.update_layout(
    yaxis=dict(categoryorder="total ascending"),
    height=500
)

st.plotly_chart(fig_profit, use_container_width=True)

st.divider()

# --------------------------------------------------
# TOP 10 PRODUCTS BY PROFIT MARGIN
# --------------------------------------------------
st.subheader("📊 Top 10 Products by Profit Margin")

margin_df = filtered_df.copy()

margin_df["Margin %"] = (
    margin_df["Gross Profit"] /
    margin_df["Sales"]
) * 100

top_margin = (
    margin_df.groupby("Product Name", as_index=False)["Margin %"]
    .mean()
    .sort_values("Margin %", ascending=False)
    .head(10)
)

fig_margin = px.bar(
    top_margin,
    x="Margin %",
    y="Product Name",
    orientation="h",
    color="Margin %",
    color_continuous_scale="Oranges"
)

fig_margin.update_layout(
    yaxis=dict(categoryorder="total ascending"),
    height=500
)

st.plotly_chart(fig_margin, use_container_width=True)

st.divider()

# --------------------------------------------------
# COST VS GROSS PROFIT SCATTER
# --------------------------------------------------
st.subheader("💰 Cost vs Gross Profit Analysis")

fig_scatter = px.scatter(
    filtered_df,
    x="Cost",
    y="Gross Profit",
    color="Division",
    hover_name="Product Name"
)

fig_scatter.update_layout(height=500)

st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# --------------------------------------------------
# EXECUTIVE BUSINESS SUMMARY
# --------------------------------------------------
st.subheader("📑 Executive Business Summary")

best_division = (
    filtered_df.groupby("Division")["Gross Profit"]
    .sum()
    .idxmax()
)

best_product = (
    filtered_df.groupby("Product Name")["Gross Profit"]
    .sum()
    .idxmax()
)

st.markdown(f"""
### Key Insights

- **Best Performing Division:** {best_division}
- **Most Profitable Product:** {best_product}
- **Total Sales:** ${total_sales:,.2f}
- **Total Gross Profit:** ${total_profit:,.2f}
- **Overall Profit Margin:** {profit_margin:.2f}%

### Recommendations

1. Increase marketing investment in **{best_division}** division.
2. Prioritize inventory for **{best_product}**.
3. Review low-margin products for pricing optimization.
4. Monitor high-cost products to improve profitability.
""")

st.divider()

# --------------------------------------------------
# DOWNLOAD FILTERED DATA
# --------------------------------------------------
st.subheader("📥 Download Filtered Dataset")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download CSV",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)