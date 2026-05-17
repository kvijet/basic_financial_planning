import streamlit as st
import pandas as pd
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
    
    expected_annual_return = st.number_input(
        "Expected Annual Return (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1
    ) / 100
    expected_monthly_return = (1 + expected_annual_return) ** (1 / 12) - 1
    
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
        
        # Calculate interest income on previous year's corpus only with monthly compounding
        # (Contribution is made at end of year, so no interest on it)
        interest_income = corpus * (((1 + expected_monthly_return) ** 12) - 1)
        
        # Calculate year end corpus
        # Year end balance = previous year corpus + interest earned + new contribution - annual expenses
        new_corpus = corpus * ((1 + expected_monthly_return) ** 12) + annual_contribution - annual_expense
        
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
    **Starting Corpus:** {current_assets:,.2f}  
    **Monthly Contribution:** {monthly_contribution:,.2f}  
    **Monthly Expense:** {current_monthly_expense:,.2f}  
    **Expected Annual Return:** {expected_annual_return*100:.2f}%  
    **Expected Inflation:** {expected_inflation*100:.2f}%
    """)
    
    if st.button("📊 Calculate SIP for a Goal", use_container_width=True):
        st.switch_page("pages/1_SIP_Calculator.py")

with col1:
    # Calculate and display results
    if calculate_button:
        df_results = calculate_wealth_plan(
            current_age, retirement_age, planning_horizon, current_assets,
            monthly_contribution, annual_contribution_increase, expected_monthly_return,
            current_monthly_expense, expected_inflation
        )
        
        st.subheader("Wealth Projection Table")        

        total_months = planning_horizon * 12
        retirement_month = (retirement_age - current_age + 1) * 12

        wealth_df=pd.DataFrame(columns=['Month','Age','Opening Balance','Running Expense','Expense','Return Earned','Contribution','Closing Balance','Deficit'])
        wealth_df['Month'] = range(1, total_months + 1)

        ages=[]
        contribution=[]
        running_expense = []
        contr = monthly_contribution
        run_expense = current_monthly_expense

        for m in wealth_df.Month:
                if m == 1:
                    age = current_age
                    contr = monthly_contribution

                if m <= retirement_month:
                    running_expense.append(0)
                elif m > retirement_month:
                    running_expense.append(run_expense)


                elif m % 12 == 1:
                    age += 1
                    if m <= retirement_month:
                        contr *= (1 + annual_contribution_increase)
                    elif m > retirement_month:
                        contr = 0

                # else keep the same age
                ages.append(age)
                contribution.append(contr)
                running_expense.append(run_expense)
                run_expense *= (1 + expected_inflation/12)  # Adjust for

        wealth_df['Age']=ages
        wealth_df['Contribution']=contribution


        st.dataframe(wealth_df, use_container_width=True, hide_index=True)

        # # Initialize lists for each column
        # months = []
        # opening_balance = []
        # expenses = []
        # returns = []
        # contributions = []
        # closing_balance = []
        # deficit = []

        # # Start with current assets
        # balance = current_assets
        # monthly_contr = monthly_contribution

        # for m in range(1, total_months + 1):
        #     months.append(m)
        #     opening_balance.append(balance)

        #     # Expense logic
        #     if m <= retirement_month:
        #         exp = 0
        #     else:
        #         # Inflation adjusted expense at retirement start
        #         months_to_retirement = retirement_month
        #         base_exp = current_monthly_expense * ((1 + expected_inflation/12) ** months_to_retirement)
        #         # Then grow each month with inflation
        #         exp = base_exp * ((1 + expected_inflation/12) ** (m - retirement_month - 1))
        #     expenses.append(exp)

        #     # Contribution logic
        #     if m <= retirement_month:
        #         # Step-up every 12 months
        #         if m % 12 == 1 and m > 1:
        #             monthly_contr *= (1 + annual_contribution_increase)
        #         contr = monthly_contr
        #     else:
        #         contr = 0
        #     contributions.append(contr)

        #     # Return earned
        #     ret = (balance - exp) * expected_monthly_return
        #     returns.append(ret)

        #     # Closing balance
        #     bal = balance - exp + ret + contr
        #     if bal < 0:
        #         deficit_val = -bal
        #         bal = 0
        #     else:
        #         deficit_val = 0
        #     closing_balance.append(bal)
        #     deficit.append(deficit_val)

        #     # Update balance for next month
        #     balance = bal

        # # Create DataFrame
        # wealth_plan = pd.DataFrame({
        #     "Month": months,
        #     "Opening Balance": opening_balance,
        #     "Expense": expenses,
        #     "Return Earned": returns,
        #     "Contribution": contributions,
        #     "Closing Balance": closing_balance,
        #     "Deficit": deficit
        # })

        # wealth_plan_display = wealth_plan.copy()
        # wealth_plan_display['Opening Balance'] = wealth_plan_display['Opening Balance'].apply(lambda x: f"{x:,.2f}")
        # wealth_plan_display['Expense'] = wealth_plan_display['Expense'].apply(lambda x: f"{x:,.2f}")
        # wealth_plan_display['Return Earned'] = wealth_plan_display['Return Earned'].apply(lambda x: f"{x:,.2f}")
        # wealth_plan_display['Contribution'] = wealth_plan_display['Contribution'].apply(lambda x: f"{x:,.2f}")
        # wealth_plan_display['Closing Balance'] = wealth_plan_display['Closing Balance'].apply(lambda x: f"{x:,.2f}")
        # wealth_plan_display['Deficit'] = wealth_plan_display['Deficit'].apply(lambda x: f"{x:,.2f}")

    #     # After wealth_plan dataframe is created
    #     final_balance = wealth_plan["Closing Balance"].iloc[-1]
    #     run_out_months = wealth_plan[wealth_plan["Closing Balance"] == 0]["Month"]

    #     if not run_out_months.empty:
    #         run_out_age = current_age + run_out_months.iloc[0] // 12
    #         years_before_end = planning_horizon - (run_out_months.iloc[0] // 12)
    #         st.warning(
    #             f"⚠️ You will run out of money at age {run_out_age}, "
    #             f"which is {years_before_end} years before the end of your plan."
    #         )
    #     else:
    #         st.success(
    #             f"✅ At the end of {planning_horizon} years, "
    #             f"you will still have {final_balance:,.2f} left."
    #         )


    #     # Display in Streamlit
    #     st.dataframe(wealth_plan_display, use_container_width=True, hide_index=True)


    #     # Download option
    #     csv = wealth_plan_display.to_csv(index=False)
    #     st.download_button(
    #         label="Download Projection (CSV)",
    #         data=csv,
    #         file_name=f"wealth_projection_{datetime.now().strftime('%Y%m%d')}.csv",
    #         mime="text/csv",
    #         on_click="ignore"
    #     )
    # else:
    #     st.info("👈 Configure your parameters in the sidebar and click 'Calculate Projection' to see the results.")
