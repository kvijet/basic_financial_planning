# Wealth Planning Calculator

A Streamlit-based wealth planning calculator that helps you project your financial situation through retirement.

## Features

- **Input Parameters**: Configure your financial situation including:
  - Current age and retirement age
  - Current assets and monthly contributions
  - Expected returns and inflation rates
  - Monthly expenses

- **Wealth Projection**: Get a year-by-year breakdown of:
  - Your annual contributions
  - Interest income earned
  - Annual expenses (before and after retirement)
  - Year-end corpus (total wealth)

- **Key Insights**: View summary metrics including final corpus, peak corpus, and sustainability status

- **Visualization**: See a line chart of your corpus growth over time

- **Export**: Download your projection as a CSV file

## Installation

1. Clone or download this repository
2. Install Python 3.8 or higher
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

```bash
streamlit run wealth_planner.py
```

The app will open in your default web browser at `http://localhost:8501`

## How It Works

### Calculation Logic

**Annual Contribution:**
- First year: Monthly contribution × 12
- Subsequent years (before retirement): Increases by "Annual Increase in Monthly Contribution" %
- From retirement year onwards: 0

**Annual Expense:**
- Before retirement: 0
- From retirement year onwards: (Current monthly expense × 12) × (1 + inflation)^years since retirement

**Year-End Corpus:**
- Year 1: (Annual contribution + Current assets) × (1 + Expected return) - Annual expense
- Year N: (Previous year corpus + Annual contribution) × (1 + Expected return) - Annual expense

**Interest Income:**
- (Previous year corpus + Current year contribution) × Expected rate of return

## Input Parameters

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| Current Age | Integer | 18-100 | 30 |
| Retirement Age | Integer | >Current Age | 60 |
| Planning Horizon | Integer | 1-100 | 40 |
| Current Assets | Float | ≥0 | $100,000 |
| Monthly Contribution | Float | ≥0 | $1,000 |
| Annual Contribution Increase | % | 0-100 | 3% |
| Expected Monthly Return | % | 0-50 | 10% |
| Current Monthly Expense | Float | >0 | $3,000 |
| Expected Inflation | % | 0-20 | 5% |

## Notes

- The calculator uses compound interest calculations based on monthly returns
- The plan is considered "Sustainable" if the final corpus is positive
- You can adjust parameters and recalculate to see how different scenarios affect your retirement
- Consider consulting a financial advisor for professional financial planning advice

## Example Scenarios

### Conservative Plan
- Annual Contribution Increase: 2%
- Expected Monthly Return: 6%
- Expected Inflation: 3%

### Moderate Plan
- Annual Contribution Increase: 3%
- Expected Monthly Return: 10%
- Expected Inflation: 5%

### Aggressive Plan
- Annual Contribution Increase: 5%
- Expected Monthly Return: 12%
- Expected Inflation: 5%
