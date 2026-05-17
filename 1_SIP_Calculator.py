import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SIP Calculator", layout="wide")
st.title("How Much Should My SIP Be?")

# Create sidebar for inputs
with st.sidebar:
    st.header("SIP Goal Parameters")
    
    expense_start_date = st.date_input(
        "When will you need this money? (Expense Start Date)",
        value=datetime.now().replace(year=datetime.now().year + 10)
    )
    
    monthly_expense = st.number_input(
        "Monthly Expense Amount",
        min_value=0.0,
        value=100000.0,
        step=5000.0
    )
    
    expense_duration_years = st.number_input(
        "How long will you need this expense? (years)",
        min_value=1,
        max_value=100,
        value=30,
        step=1
    )
    
    expense_growth_rate = st.number_input(
        "Expense Growth Rate (% per year)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=0.1
    ) / 100
    
    expected_annual_return = st.number_input(
        "Expected Annual Return (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1
    ) / 100
    
    current_assets = st.number_input(
        "Current Assets (if any)",
        min_value=0.0,
        value=0.0,
        step=10000.0
    )
    
    # Calculate SIP button
    calculate_sip_button = st.button("Calculate Required SIP", type="primary")


def calculate_required_corpus(monthly_expense, expense_growth_rate, expected_annual_return, expense_duration_years):
    """
    Calculate total corpus needed to sustain the expense
    """
    monthly_return = (1 + expected_annual_return) ** (1 / 12) - 1
    total_months = expense_duration_years * 12
    
    corpus_needed = 0
    for m in range(1, total_months + 1):
        # Monthly expense with growth
        years_passed = (m - 1) / 12
        exp = monthly_expense * ((1 + expense_growth_rate) ** years_passed)
        # Present value of this expense at start of expense period
        corpus_needed += exp / ((1 + monthly_return) ** (m - 1))
    
    return corpus_needed


def calculate_required_sip(target_corpus, current_assets, months_to_goal, expected_annual_return):
    """
    Calculate the monthly SIP needed to reach target corpus
    Using Future Value of SIP formula
    """
    monthly_return = (1 + expected_annual_return) ** (1 / 12) - 1
    
    # Growth of current assets
    future_current_assets = current_assets * ((1 + monthly_return) ** months_to_goal)
    
    # Remaining amount needed from SIP
    remaining_needed = target_corpus - future_current_assets
    
    if remaining_needed <= 0:
        return 0
    
    # SIP calculation: FV = SIP * [((1+r)^n - 1) / r]
    # Therefore: SIP = FV / [((1+r)^n - 1) / r]
    if monthly_return == 0:
        required_sip = remaining_needed / months_to_goal
    else:
        fv_factor = (((1 + monthly_return) ** months_to_goal) - 1) / monthly_return
        required_sip = remaining_needed / fv_factor
    
    return required_sip


# Main content
if calculate_sip_button:
    # Calculate months until goal
    today = datetime.now()
    months_to_goal = int((expense_start_date.year - today.year) * 12 + (expense_start_date.month - today.month))
    
    if months_to_goal < 0:
        st.error("❌ Expense start date must be in the future!")
    else:
        years_to_goal = months_to_goal / 12
        
        # Calculate required corpus at expense start date
        required_corpus = calculate_required_corpus(
            monthly_expense, expense_growth_rate, expected_annual_return, expense_duration_years
        )
        
        # Calculate required SIP
        required_sip = calculate_required_sip(
            required_corpus, current_assets, months_to_goal, expected_annual_return
        )
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Goal Summary")
            st.info(f"""
            **Expense Start Date:** {expense_start_date.strftime('%B %d, %Y')}  
            **Time to Goal:** {years_to_goal:.1f} years  
            **Monthly Expense:** {monthly_expense:,.2f}  
            **Expense Growth Rate:** {expense_growth_rate*100:.2f}%  
            **Expense Duration:** {expense_duration_years} years  
            **Expected Annual Return:** {expected_annual_return*100:.2f}%  
            **Current Assets:** {current_assets:,.2f}
            """)
        
        with col2:
            st.subheader("Results")
            st.metric("Total Corpus Needed", f"{required_corpus:,.2f}")
            st.metric("Growth of Current Assets", f"{current_assets * (((1 + expected_annual_return) ** (1/12)) - 1) ** months_to_goal:,.2f}")
            st.metric("Required Monthly SIP", f"{required_sip:,.2f}", delta=None)
        
        # Detailed breakdown
        st.subheader("📊 Detailed Breakdown")
        
        monthly_return = (1 + expected_annual_return) ** (1 / 12) - 1
        
        # Calculate month-by-month growth
        months_list = []
        sip_amounts = []
        opening_balance = []
        sip_invested = []
        returns = []
        closing_balance = []
        
        balance = current_assets
        
        for m in range(1, months_to_goal + 1):
            months_list.append(m)
            opening_balance.append(balance)
            
            # SIP invested
            sip_amt = required_sip
            sip_invested.append(sip_amt)
            
            # Returns
            ret = balance * monthly_return
            returns.append(ret)
            
            # Closing balance
            closing = balance + sip_amt + ret
            closing_balance.append(closing)
            
            balance = closing
        
        # Create DataFrame
        sip_projection = pd.DataFrame({
            "Month": months_list,
            "Opening Balance": opening_balance,
            "SIP Invested": sip_invested,
            "Returns": returns,
            "Closing Balance": closing_balance
        })
        
        # Format for display
        sip_display = sip_projection.copy()
        sip_display['Opening Balance'] = sip_display['Opening Balance'].apply(lambda x: f"{x:,.2f}")
        sip_display['SIP Invested'] = sip_display['SIP Invested'].apply(lambda x: f"{x:,.2f}")
        sip_display['Returns'] = sip_display['Returns'].apply(lambda x: f"{x:,.2f}")
        sip_display['Closing Balance'] = sip_display['Closing Balance'].apply(lambda x: f"{x:,.2f}")
        
        # Show every 12th row (yearly view)
        yearly_display = sip_display.iloc[11::12].reset_index(drop=True)
        st.dataframe(yearly_display, use_container_width=True, hide_index=True)
        
        # Summary message
        st.success(
            f"✅ To accumulate **{required_corpus:,.2f}** by **{expense_start_date.strftime('%B %d, %Y')}**, "
            f"you need to invest a monthly SIP of **{required_sip:,.2f}**"
        )
        
        # Download option
        csv = sip_display.to_csv(index=False)
        st.download_button(
            label="Download Full Projection (CSV)",
            data=csv,
            file_name=f"sip_projection_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
else:
    st.info("👈 Enter your goal parameters in the sidebar and click 'Calculate Required SIP' to see results.")
