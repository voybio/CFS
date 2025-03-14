# src/ui.py
import streamlit as st
import pandas as pd
import altair as alt
from src.business_logic import calculate_financials
from src.utils import load_config
# from src.data import DEFAULT_NEW_CUSTOMERS # Remove this line

def run_app():
    # Load configuration (e.g. app title) from .env
    config = load_config()
    st.title(config.get("APP_TITLE", "Financial Simulator"))

    with st.sidebar:
        with st.expander("Cost Inputs", expanded=True):
            operating_expenses = st.number_input("Operating Expenses (annual) ($)", value=524000, step=10000)
            annual_loan_repayment = st.number_input("Annual Loan Repayment (Years 1-5) ($)", value=553750, step=10000)
            owner_payout_year1 = st.number_input("Owner Payout Year 1 ($)", value=525000, step=10000)
            owner_payout_year2 = st.number_input("Owner Payout Year 2 ($)", value=520000, step=10000)
            loan_principal = st.number_input("Loan Principal ($)", value=2500000, step=100000)

        with st.expander("Revenue Inputs", expanded=True):
            direct_fee = st.number_input("Direct Customer Annual Rev ($)", value=39000, step=1000)
            affiliation_gross_fee = st.number_input("Affiliation Gross Rev ($)", value=35000, step=1000)
            affiliation_referral_fee = st.number_input("Affiliation Referral Fee ($)", value=7000, step=500)
            channel_b_new_rev = st.number_input("Outconvert Revenue ($)", value=10000, step=500)
            channel_b_retained_rev = st.number_input("Outconvert Revenue Retained Revenue ($)", value=4000, step=500)
            direct_retention = st.slider("Direct Retention Rate", 0.0, 1.0, 0.9, 0.05, key="direct_retention_main")
            affiliation_retention = st.slider("Affiliation Retention Rate", 0.0, 1.0, 0.75, 0.05, key="affiliation_retention_main")
            channel_b_retention = st.slider("Outconvert Revenue Rate", 0.0, 1.0, 0.7, 0.05, key="channel_b_retention_main")

            st.header("New Customers per Year")
            years = list(range(1, 8))
            new_customers = {}
            default_values = {}  # DEFAULT_NEW_CUSTOMERS  # imported from src/data.py
            for y in years:
                new_customers[y] = st.number_input(
                    f"Year {y} New Customers", value=10, step=1
                )

            st.header("Yearly Retention Rates")
            direct_retention_by_year = {}
            affiliation_retention_by_year = {}
            for y in years:
                direct_retention_by_year[y] = st.slider(f"Year {y} Direct Retention Rate", 0.0, 1.0, 0.9, 0.05, key=f"direct_retention_{y}")
                affiliation_retention_by_year[y] = st.slider(f"Year {y} Affiliation Retention Rate", 0.0, 1.0, 0.75, 0.05, key=f"affiliation_retention_{y}")

            st.header("Referral Fee Percentage")
            affiliation_referral_pct = st.slider("Affiliation Referral Fee (%)", 0.0, 1.0, 0.2, 0.05, key="affiliation_referral_pct_main")
            affiliation_net_fee = affiliation_gross_fee * (1 - affiliation_referral_pct)

            st.header("Additional Referrals Input")
            additional_referrals_per_year = {}
            for y in years:
                additional_referrals_per_year[y] = st.number_input(f"Year {y} Additional Referral Volume", value=10, step=1)

    # Bundle parameters into a dictionary
    params = {
        "direct_fee": direct_fee,
        "affiliation_gross_fee": affiliation_gross_fee,
        "affiliation_referral_fee": affiliation_referral_fee,
        "affiliation_net_fee": affiliation_net_fee,
        "channel_b_new_rev": channel_b_new_rev,
        "channel_b_retained_rev": channel_b_retained_rev,
        "direct_retention": direct_retention,
        "affiliation_retention": affiliation_retention,
        "channel_b_retention": channel_b_retention,
        "new_customers": new_customers,
        "operating_expenses": operating_expenses,
        "annual_loan_repayment": annual_loan_repayment,
        "owner_payout_year1": owner_payout_year1,
        "owner_payout_year2": owner_payout_year2,
        "loan_principal": loan_principal,
        "direct_retention_by_year": direct_retention_by_year,
        "affiliation_retention_by_year": affiliation_retention_by_year,
        "affiliation_referral_pct": affiliation_referral_pct,
        "additional_referrals_per_year": additional_referrals_per_year
    }

    # Compute financials using business logic
    df = calculate_financials(params)

    st.header("Financial Projections")
    st.dataframe(df)

    # Altair chart: Interactive line chart for Revenue vs. Expenses vs. Net Profit
    chart_data = df.melt(id_vars=["Year"], value_vars=["Total Revenue", "Total Expenses", "Net Profit"],
                         var_name="Metric", value_name="Amount")
    chart = alt.Chart(chart_data).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Amount:Q", title="Amount ($)"),
        color="Metric:N",
        tooltip=["Year", "Metric", "Amount"]
    ).properties(title="Revenue vs. Expenses vs. Net Profit")
    st.altair_chart(chart, use_container_width=True)
