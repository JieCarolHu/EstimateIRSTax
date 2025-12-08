import pandas as pd
import xlwings as xw
import sys
import os
from win32com.client import constants

# --- Constant arrays for dividend classification ---
qualifiedDividendSymbols = [
    "AAPL",
    "Apple Inc",
    "MSFT",
    "Microsoft Corp",
    "Eaton",
    "Nvidia",
    "SPY",
    "Dividend Reinvestment – Long-term Growth",
    "Q4 2024 Dividends",
    "2025 Dividends",
    "Nav Distribution",
    "S&p 500 Etf",
    "Splg",
    "Qqq",
    "Select Sector Spdr Trust Technology",
    "Invesco Nasdaq 100 Etf",
    "Xlk",
    "Googl",
    "Baron Partners Fund - Long-term Cap Gain", # this is long term gain, but taxed as qualified div.
]  # example qualified symbols

unqualifiedDividendSymbols = [
    "Fidelity Government Money Market",
    "Fdrxx",
    "Allspring",
    "Ishares 0-3 Month Treasury Bond Etf",
    "3 Mnth Treasury Bnd Etf",
    "3 Mnth Treasry",
    "Sgov",
    "Wisdomtree Japan Hedged",
    "Dxj"
]  # example unqualified symbols

interestShownAsInvestmentIncome = [
    "Interest",
    "Fully Paid - Interest Fully Paid",
    "Cad Credit Int",
]  # example interest descriptions


# Ensure results folder exists
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)
# Build output path
output_excel_path = os.path.join(results_dir, "output.xlsx")

try:
    # Try opening the file in exclusive mode
    with open(output_excel_path, 'r+', encoding='utf-8'):
        pass
except PermissionError:
    raise RuntimeError(f"❌ The file '{output_excel_path}' appears to be open in Excel. Please close it and try again.")
except FileNotFoundError:
    # Ignore if the file does not exist
    pass

# Check for input argument
if len(sys.argv) < 2:
    print("Usage: python calcTaxableInvestIncome.py <input_file.csv>")
    sys.exit(1)

input_file = sys.argv[1]

# Validate file existence
if not os.path.isfile(input_file):
    print(f"Error: File '{input_file}' not found.")
    sys.exit(1)

# Load the CSV
df = pd.read_csv(input_file)

# Normalize column names
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Normalize category values
if 'category' in df.columns:
    df['category'] = df['category'].str.strip().str.lower()

# --- Dividend classification based on description ---
for idx, row in df.iterrows():
    if "investment income" == str(row["category"]).lower():
        desc = str(row['description'])
        date = str(row['date'])
        account = str(row['account'])
        amount = str(row['amount'])
        matched = False
        for sym in interestShownAsInvestmentIncome:
            if sym.lower() in desc.lower():
                df.loc[idx, 'category'] = 'interest'
                matched = True
                print (f"🟦 {date} - {account} - {amount} - {desc} - interest ")
        for sym in unqualifiedDividendSymbols:
            if sym.lower() in desc.lower():
                if matched == True: 
                    raise RuntimeError(f"❌ Conflict in classification for '{desc}' matched both interest and unqualified div.")
                
                df.loc[idx, 'category'] = 'unqualified_div'
                matched = True
                print (f"⬜ {date} - {account} - {amount} - {desc} - unqualified_div ")
                break
        for sym in qualifiedDividendSymbols:
            if sym.lower() in desc.lower():
                if matched == True: 
                    raise RuntimeError(f"❌ Conflict in classification for '{desc}' matched both interest/unqualified div and qualified div.")
                
                df.loc[idx, 'category'] = 'qualified_div'
                matched = True
                print (f"🟨 {date} - {account} - {amount} - {desc} - qualified_div ")
                break

        if not matched:
            print(
                f"❌ Investment income: {date} - {account} - {amount} - '{desc}' does not match any defined qualified or unqualified symbols."
            )
            
# make sure all "investment income" have been classified
for idx, row in df.iterrows():
    if "investment income" == str(row["category"]).lower():
        raise RuntimeError(f"❌{str(row['category'])} Dividend description '{str(row['description'])}' does not match any defined qualified or unqualified symbols.")
           
# Filter for relevant categories (include dividends)
filtered = df[df['category'].isin(['qualified_div', 'unqualified_div', 'interest'])]
filtered.to_excel("filter.xlsx", index=False)

# Group and sum
summary = filtered.groupby(['account', 'category'])['amount'].sum().unstack(fill_value=0).reset_index()

# Add taxable column -- exclude the qualified_div
def compute_taxable(row):
    account = row['account']
    if 'IRA' not in account and 'HSA' not in account:
        return round(
            row.get('unqualified_div', 0) +
            row.get('interest', 0), 2
        )
    return 0.0

summary['taxable'] = summary.apply(compute_taxable, axis=1)

# Save to Excel first (without total row)
summary.to_excel(output_excel_path, index=False)

print(f"✅ Summary saved to {output_excel_path}")


# Load workbook and add formula row
wb = xw.Book(output_excel_path)
ws = wb.sheets[0]

# Define the range
last_row = ws.range("A1").end("down").row
last_col = ws.range("A1").end("right").column
table_range = ws.range((1, 1), (last_row, last_col))

# Format as table
table = ws.api.ListObjects.Add(1, table_range.api, 0, 1)
table.Name = "FinancialSummary"
table.TableStyle = "TableStyleMedium9"
table.ShowTotals = True

# Use constants for TotalsCalculation
table.ListColumns(5).TotalsCalculation = constants.xlTotalsCalculationSum

# Autofit all columns
ws.autofit('columns')

wb.save()
print("✅ Total row added with formulas and styled as a table.")
