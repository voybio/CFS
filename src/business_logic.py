# src/business_logic.py
import pandas as pd

def calculate_financials(params):
    """
    Calculate yearly financial metrics based on input parameters.
    Returns a DataFrame with results for Years 1 to 7.
    """
    years = list(range(1, 8))
    results = []
    
    # Starting cumulative cash from loan principal
    cumulative_cash = params.get("loan_principal", 2500000)
    
    # Initialize previous year's totals for retention calculations
    prev_total_direct = 0
    prev_total_affiliation = 0
    
    for year in years:
        new_cust = params["new_customers"].get(year, 0)
        direct_split = new_cust * 0.4
        affiliation_split = new_cust * 0.6
        
        retained_direct = prev_total_direct * params["direct_retention_by_year"][year] if year > 1 else 0
        retained_affiliation = prev_total_affiliation * params["affiliation_retention_by_year"][year] if year > 1 else 0
        
        total_direct = direct_split + retained_direct
        total_affiliation = affiliation_split + retained_affiliation
        total_customers = total_direct + total_affiliation
        
        direct_revenue = total_direct * params["direct_fee"]
        affiliation_net_revenue = total_affiliation * params["affiliation_net_fee"]
        
        # Use input for additional referrals, removing special channel naming
        additional_referrals = params["additional_referrals_per_year"][year]
        additional_referral_revenue = additional_referrals * params["channel_b_new_rev"]
        
        total_revenue = direct_revenue + affiliation_net_revenue + additional_referral_revenue
        
        # Financing costs: Years 1-2 include owner payout, Years 3-5 only loan, Years 6-7 none
        if year == 1:
            financing_cost = params["annual_loan_repayment"] + params["owner_payout_year1"]
        elif year == 2:
            financing_cost = params["annual_loan_repayment"] + params["owner_payout_year2"]
        elif year <= 5:
            financing_cost = params["annual_loan_repayment"]
        else:
            financing_cost = 0
            
        total_expenses = params["operating_expenses"] + financing_cost
        
        profit_before_tax = total_revenue - total_expenses
        tax = profit_before_tax * 0.25 if profit_before_tax > 0 else 0
        post_tax_profit = profit_before_tax - tax
        bonus = post_tax_profit * 0.08 if post_tax_profit > 0 else 0
        net_profit = post_tax_profit - bonus
        
        cumulative_cash += net_profit
        
        results.append({
            "Year": year,
            "New Customers": new_cust,
            "New Direct": direct_split,
            "Retained Direct": retained_direct,
            "Total Direct": total_direct,
            "New Affiliation": affiliation_split,
            "Retained Affiliation": retained_affiliation,
            "Total Affiliation": total_affiliation,
            "Total Customers": total_customers,
            "Direct Revenue": direct_revenue,
            "Affiliation Net Revenue": affiliation_net_revenue,
            "Channel B Revenue": additional_referral_revenue,
            "Total Revenue": total_revenue,
            "Operating Costs": params["operating_expenses"],
            "Financing Costs": financing_cost,
            "Total Expenses": total_expenses,
            "Profit Before Tax": profit_before_tax,
            "Tax": tax,
            "Post-Tax Profit": post_tax_profit,
            "Bonus": bonus,
            "Net Profit": net_profit,
            "Cumulative Cash": cumulative_cash
        })
        
        # Update previous totals for next year's retention
        prev_total_direct = total_direct
        prev_total_affiliation = total_affiliation
        
    return pd.DataFrame(results)
