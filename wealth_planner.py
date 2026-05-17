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
        step=1,
        help="The age until you plan to work or contribute to your wealth. After this age, contributions will stop and expenses will start."
    )
    
    planning_horizon = st.number_input(
        "Planning Horizon (years)",
        min_value=1,
        max_value=100,
        value=60,
        step=1,
        help="The total number of years you want to plan for. This should ideally be at least as long as the number of years from your current age to your expected lifespan."
    )
    
    current_assets = st.number_input(
        "Current Assets",
        min_value=0.0,
        value=1000000.0,
        step=1000.0,
        format ="{x:,.2f}",
        help="The total value of your current savings and investments that will be used as the starting point for your wealth projection."
    )
    
    monthly_contribution = st.number_input(
        "Monthly Contribution",
        min_value=0.0,
        value=50000.0,
        step=5000.0,
        format ="{x:,.2f}",
        help="The amount you plan to contribute to your wealth every month until retirement. This can be adjusted for annual increases in the next input."
    )
    
    annual_contribution_increase = st.number_input(
        "Annual Increase in Monthly Contribution (%)",
        min_value=0.0,
        max_value=100.0,
        value=3.0,
        step=0.1,
        help="The percentage by which your monthly contribution will increase each year."
    ) / 100
    
    expected_annual_return = st.number_input(
        "Expected Annual Return (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
        help="The expected annual return on your investments."
    ) / 100
    expected_monthly_return = (1 + expected_annual_return) ** (1 / 12) - 1
    
    current_monthly_expense = st.number_input(
        "Current Monthly Expense",
        min_value=0.0,
        value=75000.0,
        step=5000.0,
        format ="{x:,.2f}",
        help="Your current monthly expenses that will need to be covered during retirement. This will be adjusted for inflation in the projection."
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
    #Calculate and display results
    if calculate_button:
        
        st.subheader("Wealth Projection Table")        

        total_months = (planning_horizon + 1) * 12
        retirement_month = (retirement_age - current_age + 1) * 12

        wealth_df=pd.DataFrame(columns=['Month','Age','Opening Balance','Expense','Return Earned','Contribution','Closing Balance','Deficit'])
        
        wealth_df['Month'] = range(1, total_months + 1)

        ages=[]
        contribution=[]
        contr = monthly_contribution
        monthly_exp = current_monthly_expense
        exp =[]

        for m in wealth_df.Month:
                if m > retirement_month:
                    exp.append(monthly_exp)

                elif m <= retirement_month:
                    exp.append(0)
                    

                monthly_exp *= ((1 + expected_inflation)**(1/12))

                if m == 1:
                    age = current_age
                    contr = monthly_contribution

                elif m % 12 == 1:
                    age += 1
                    if m <= retirement_month:
                        contr *= (1 + annual_contribution_increase)
                    elif m > retirement_month:
                        contr = 0

                # else keep the same age
                ages.append(age)
                contribution.append(contr)
                
        wealth_df['Age']=ages
        wealth_df['Contribution']=contribution
        wealth_df['Expense']=exp

        balance = current_assets

        for i in range(len(wealth_df)):
            # Opening balance
            wealth_df.at[i, 'Opening Balance'] = balance
            
            # Return earned
            wealth_df.at[i, 'Return Earned'] = balance * expected_monthly_return
            
            # Closing balance
            bal = balance + wealth_df.at[i, 'Return Earned'] \
                        + wealth_df.at[i, 'Contribution'] \
                        - wealth_df.at[i, 'Expense']
            
            if bal < 0:
                wealth_df.at[i, 'Closing Balance'] = 0
                wealth_df.at[i, 'Deficit'] = -bal
            else:
                wealth_df.at[i, 'Closing Balance'] = bal
                wealth_df.at[i, 'Deficit'] = 0
            
            # Update balance for next iteration
            balance = wealth_df.at[i, 'Closing Balance']

        wealth_plan_display = wealth_df.copy()
        wealth_plan_display['Opening Balance'] = wealth_plan_display['Opening Balance'].apply(lambda x: f"{x:,.2f}")
        wealth_plan_display['Expense'] = wealth_plan_display['Expense'].apply(lambda x: f"{x:,.2f}")
        wealth_plan_display['Return Earned'] = wealth_plan_display['Return Earned'].apply(lambda x: f"{x:,.2f}")
        wealth_plan_display['Contribution'] = wealth_plan_display['Contribution'].apply(lambda x: f"{x:,.2f}")
        wealth_plan_display['Closing Balance'] = wealth_plan_display['Closing Balance'].apply(lambda x: f"{x:,.2f}")
        wealth_plan_display['Deficit'] = wealth_plan_display['Deficit'].apply(lambda x: f"{x:,.2f}")

        st.dataframe(wealth_plan_display, use_container_width=True, hide_index=True)

        # Download option
        csv = wealth_plan_display.to_csv(index=False)
        st.download_button(
            label="Download Projection (CSV)",
            data=csv,
            file_name=f"wealth_projection_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            on_click="ignore"
        )        

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
