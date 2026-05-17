import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

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
        step=10000.0,
        help="The total value of your current savings and investments that will be used as the starting point for your wealth projection."
    )
    
    monthly_contribution = st.number_input(
        "Monthly Contribution",
        min_value=0.0,
        value=50000.0,
        step=5000.0,
        help="The amount you plan to contribute to your wealth every month until retirement. This can be adjusted for annual increases in the next input."
    )
    
    annual_contribution_increase = st.number_input(
        "Annual Increase in Monthly Contribution (%)",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=1.0,
        help="The percentage by which your monthly contribution will increase each year."
    ) / 100
    
    expected_annual_return = st.number_input(
        "Expected Annual Return (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=1.0,
        help="The expected annual return on your investments."
    ) / 100
    expected_monthly_return = (1 + expected_annual_return) ** (1 / 12) - 1
    
    current_monthly_expense = st.number_input(
        "Current Monthly Expense",
        min_value=0.0,
        value=75000.0,
        step=5000.0,
        help="Your current monthly expenses that will need to be covered during retirement. This will be adjusted for inflation in the projection."
    )
    
    expected_inflation = st.number_input(
        "Expected Inflation (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=1.0
    ) / 100

    # Calculate Projection button at the end of sidebar
    calculate_button = st.button("Calculate Projection", type="primary")

# Main content area
col1, col2 = st.columns([2, 1])


#Calculate and display results
if calculate_button:

    st.subheader("Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **Retirement Age:** {retirement_age}  
        **Years to Retirement:** {retirement_age - current_age}  
        **Planning Horizon:** {planning_horizon} years  
        **Starting Corpus:** {current_assets:,.2f}  

        """)

    with col2:
        st.info(f"""
        **Monthly Contribution:** {monthly_contribution:,.2f}  
        **Monthly Expense:** {current_monthly_expense:,.2f}  
        **Expected Annual Return:** {expected_annual_return*100:.2f}%  
        **Expected Inflation:** {expected_inflation*100:.2f}%
        """)        
           

    total_months = (planning_horizon + 1) * 12
    retirement_month = (retirement_age - current_age + 1) * 12

    wealth_df=pd.DataFrame(columns=['Month','Age','Opening Balance','Expense','Return Earned','Contribution','Closing Balance','Monthly Deficit'])
    
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
            wealth_df.at[i, 'Monthly Deficit'] = bal
        else:
            wealth_df.at[i, 'Closing Balance'] = bal
            wealth_df.at[i, 'Monthly Deficit'] = 0
        
        # Update balance for next iteration
        balance = wealth_df.at[i, 'Closing Balance']

    wealth_df['Net Cash Flow'] = wealth_df['Contribution'] - wealth_df['Expense']

    wealth_plan_display = wealth_df.copy()
    wealth_plan_display.drop(columns=['Net Cash Flow'], inplace=True)
    wealth_plan_display['Opening Balance'] = wealth_plan_display['Opening Balance'].apply(lambda x: f"{x:,.2f}")
    wealth_plan_display['Expense'] = wealth_plan_display['Expense'].apply(lambda x: f"{x:,.2f}")
    wealth_plan_display['Return Earned'] = wealth_plan_display['Return Earned'].apply(lambda x: f"{x:,.2f}")
    wealth_plan_display['Contribution'] = wealth_plan_display['Contribution'].apply(lambda x: f"{x:,.2f}")
    wealth_plan_display['Closing Balance'] = wealth_plan_display['Closing Balance'].apply(lambda x: f"{x:,.2f}")
    wealth_plan_display['Monthly Deficit'] = wealth_plan_display['Monthly Deficit'].apply(lambda x: f"{x:,.2f}")

    if len(wealth_df[wealth_df['Closing Balance'] == 0].head(1))>0:
        summary_df=pd.concat([wealth_df[wealth_df['Closing Balance'] == 0].head(1),wealth_df.tail(1)])
    
    else:
        summary_df = wealth_df.tail(1)

    if len(wealth_df[wealth_df['Closing Balance'] == 0].head(1))>0:
        st.warning(f"Based on the current parameters, your wealth will be depleted by age {int(wealth_df[wealth_df['Closing Balance'] == 0].head(1)['Age'].values[0])}. Consider adjusting your contributions, expected returns, or expenses to ensure a more sustainable plan.")   

    summary_df_display = summary_df.copy()
    summary_df_display.drop(columns=['Net Cash Flow'], inplace=True)
    summary_df_display['Opening Balance'] = summary_df_display['Opening Balance'].apply(lambda x: f"{x:,.2f}")
    summary_df_display['Expense'] = summary_df_display['Expense'].apply(lambda x: f"{x:,.2f}")
    summary_df_display['Return Earned'] = summary_df_display['Return Earned'].apply(lambda x: f"{x:,.2f}")
    summary_df_display['Contribution'] = summary_df_display['Contribution'].apply(lambda x: f"{x:,.2f}")
    summary_df_display['Closing Balance'] = summary_df_display['Closing Balance'].apply(lambda x: f"{x:,.2f}")
    summary_df_display['Monthly Deficit'] = summary_df_display['Monthly Deficit'].apply(lambda x: f"{x:,.2f}")

    st.subheader("Wealth Projection Summary") 
    st.dataframe(summary_df_display, use_container_width=True, hide_index=True)



# Visualization of Net Cash Flow and Closing Balance

# "Month", "Net Cash Flow", "Closing Balance"

    fig, ax = plt.subplots(figsize=(10, 6))

    # Line plot for Net Cash Flow
    ax.plot(
        wealth_df["Month"],
        wealth_df["Net Cash Flow"],
        label="Net Cash Flow",
        color="blue",
        linewidth=2
    )

    # Area plot for Closing Balance
    ax.fill_between(
        wealth_df["Month"],
        wealth_df["Closing Balance"],
        color="green",
        alpha=0.3,
        label="Closing Balance"
    )

    # X-axis ticks every 24 months
    ax.set_xticks(range(0, wealth_df["Month"].max() + 1, 24))

    # Labels and title
    ax.set_xlabel("Month")
    ax.set_ylabel("Value")
    ax.set_title("Wealth Planning: Cash Flow vs Closing Balance")

    # Grid and legend
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend()

# End of visualization code

    # Render in Streamlit
    st.subheader("Planning Horizon Visualization")
    st.pyplot(fig)

    st.subheader("Wealth Projection Table")
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