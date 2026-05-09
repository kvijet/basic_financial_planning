import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Wealth Planning Calculator", layout="wide")
st.title("Wealth Planning Calculator")

# Create sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")
    
    current_age = st.number_input(
        "Current Age",
        min_value=18,
        max_value=100,
        value=30,
        step=1
    )
    
    retirement_age = st.number_input(
        "Retirement Age",
        min_value=current_age + 1,
        max_value=100,
        value=60,
        step=1
    )
    
    planning_horizon = st.number_input(
        "Planning Horizon (years)",
        min_value=1,
        max_value=100,
        value=60,
        step=1
    )
    
    current_assets = st.number_input(
        "Current Assets",
        min_value=0.0,
        value=1000000.0,
        step=1000.0
    )
    
    monthly_contribution = st.number_input(
        "Monthly Contribution",
        min_value=0.0,
        value=50000.0,
        step=5000.0
    )
    
    annual_contribution_increase = st.number_input(
        "Annual Increase in Monthly Contribution (%)",
        min_value=0.0,
        max_value=100.0,
        value=3.0,
        step=0.1
    ) / 100
    
    expected_monthly_return = st.number_input(
        "Expected Monthly Return (%)",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=0.1
    ) / 100
    
    current_monthly_expense = st.number_input(
        "Current Monthly Expense",
        min_value=0.0,
        value=75000.0,
        step=5000.0
    )
    
    expected_inflation = st.number_input(
        "Expected Inflation (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=0.1
    ) / 100

    # Calculate Projection button at the end of sidebar
    calculate_button = st.button("Calculate Projection", type="primary")


def calculate_wealth_plan(current_age, retirement_age, planning_horizon, current_assets,
                         monthly_contribution, annual_contribution_increase, expected_monthly_return,
                         current_monthly_expense, expected_inflation):
    """
    Calculate wealth projection based on input parameters
    """
    
    current_year = datetime.now().year
    years_to_retirement = retirement_age - current_age
    
    # Initialize lists to store results
    years = []
    ages = []
    annual_contributions = []
    interest_incomes = []
    year_end_corpuses = []
    annual_expenses = []
    
    corpus = current_assets
    current_monthly_contrib = monthly_contribution
    
    for year_index in range(planning_horizon + 1):
        year = current_year + year_index
        age = current_age + year_index
        
        # Calculate annual contribution
        if age < retirement_age:
            annual_contribution = current_monthly_contrib * 12
        else:
            annual_contribution = 0
        
        # Calculate annual expense
        if age < retirement_age:
            annual_expense = 0
        else:
            # Years from current year (for inflation adjustment)
            years_from_current = age - current_age
            # Retirement expense = current monthly expense * 12, adjusted for inflation from now until each year
            # First retirement year: (current_monthly_expense * 12) * (1 + inflation)^years_to_retirement
            # Next years: continues to grow with inflation
            annual_expense = (current_monthly_expense * 12) * ((1 + expected_inflation) ** years_from_current)
        
        # Calculate interest income on previous corpus + current contribution
        interest_income = (corpus + annual_contribution) * expected_monthly_return
        
        # Calculate year end corpus
        new_corpus = (corpus + annual_contribution) * (1 + expected_monthly_return) - annual_expense
        
        # Ensure corpus doesn't go negative (but allow it for demonstration)
        # Uncomment next line if you want to stop at 0
        # new_corpus = max(0, new_corpus)
        
        years.append(year)
        ages.append(age)
        annual_contributions.append(annual_contribution)
        interest_incomes.append(interest_income)
        year_end_corpuses.append(new_corpus)
        annual_expenses.append(annual_expense)
        
        # Update for next iteration
        corpus = new_corpus
        
        # Increase monthly contribution for next year (but not if retired)
        if age < retirement_age:
            current_monthly_contrib = current_monthly_contrib * (1 + annual_contribution_increase)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Year': years,
        'Age': ages,
        'Annual Contribution': annual_contributions,
        'Interest Income': interest_incomes,
        'Annual Expense': annual_expenses,
        'Year End Corpus': year_end_corpuses
    })
    
    return df


# Main content area
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("Summary")
    st.info(f"""
    **Retirement Age:** {retirement_age}  
    **Years to Retirement:** {retirement_age - current_age}  
    **Planning Horizon:** {planning_horizon} years  
    **Starting Corpus:** ${current_assets:,.2f}  
    **Monthly Contribution:** ${monthly_contribution:,.2f}  
    **Monthly Expense:** ${current_monthly_expense:,.2f}  
    **Expected Return:** {expected_monthly_return*100:.2f}%  
    **Expected Inflation:** {expected_inflation*100:.2f}%
    """)

with col1:
    # Calculate and display results
    if calculate_button:
        df_results = calculate_wealth_plan(
            current_age, retirement_age, planning_horizon, current_assets,
            monthly_contribution, annual_contribution_increase, expected_monthly_return,
            current_monthly_expense, expected_inflation
        )
        
        st.subheader("Wealth Projection Table")
        
        # Format the dataframe for display
        df_display = df_results.copy()
        df_display['Annual Contribution'] = df_display['Annual Contribution'].apply(lambda x: f"{x:,.2f}")
        df_display['Interest Income'] = df_display['Interest Income'].apply(lambda x: f"{x:,.2f}")
        df_display['Annual Expense'] = df_display['Annual Expense'].apply(lambda x: f"{x:,.2f}")
        df_display['Year End Corpus'] = df_display['Year End Corpus'].apply(lambda x: f"{x:,.2f}")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Key insights
        st.subheader("Key Insights")
        
        final_corpus = df_results['Year End Corpus'].iloc[-1]
        max_corpus = df_results['Year End Corpus'].max()
        min_corpus = df_results['Year End Corpus'].min()
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("Final Corpus", f"${final_corpus:,.2f}")
        
        with col_b:
            st.metric("Peak Corpus", f"${max_corpus:,.2f}")
        
        with col_c:
            color = "green" if final_corpus > 0 else "red"
            status = "Sustainable" if final_corpus > 0 else "Unsustainable"
            st.metric("Plan Status", status)

        # Download option
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="Download Projection (CSV)",
            data=csv,
            file_name=f"wealth_projection_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("👈 Configure your parameters in the sidebar and click 'Calculate Projection' to see the results.")
