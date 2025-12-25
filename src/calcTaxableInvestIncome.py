import pandas as pd
import xlwings as xw
import sys
import os
from win32com.client import constants

# --- Constant arrays for dividend classification ---
qualifiedDividendSymbols = [
    "AAPL", "Apple Inc", "MSFT", "Microsoft Corp", "Eaton", "Nvidia", "SPY",
    "Dividend Reinvestment – Long-term Growth", "Q4 2024 Dividends", "2025 Dividends",
    "Nav Distribution", "S&p 500 Etf", "Splg", "Qqq", "Select Sector Spdr Trust Technology",
    "Invesco Nasdaq 100 Etf", "Xlk", "Select Sector Spdr Trust State Street Technology Select Sector Spdr Etf", "Googl",
    "Baron Partners Fund - Long-term Cap Gain"
]

unqualifiedDividendSymbols = [
    "Fidelity Government Money Market", "Fdrxx", "Allspring",
    "Ishares 0-3 Month Treasury Bond Etf", "3 Mnth Treasury Bnd Etf",
    "3 Mnth Treasry", "Sgov", "Wisdomtree Japan Hedged", "Dxj"
]

interestShownAsInvestmentIncome = [
    "Interest", "Fully Paid - Interest Fully Paid", "Cad Credit Int"
]

tabNameTaxDeferred = "TaxDeferred"
tabNameTaxable = "Taxable"

# Ensure results folder exists
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)
output_excel_path = os.path.join(results_dir, "output.xlsx")

try:
    with open(output_excel_path, 'r+', encoding='utf-8'):
        pass
except PermissionError:
    raise RuntimeError(f"❌ The file '{output_excel_path}' appears to be open in Excel. Please close it and try again.")
except FileNotFoundError:
    pass

# Check for input argument
if len(sys.argv) < 2:
    print("Usage: python calcTaxableInvestIncome.py <input_file.csv>")
    sys.exit(1)

input_file = sys.argv[1]
if not os.path.isfile(input_file):
    print(f"Error: File '{input_file}' not found.")
    sys.exit(1)

# Load CSV
df = pd.read_csv(input_file)
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
if 'category' in df.columns:
    df['category'] = df['category'].str.strip().str.lower()

# --- Classification ---
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
                print(f"🟦 {date} - {account} - {amount} - {desc} - interest ")

        for sym in unqualifiedDividendSymbols:
            if sym.lower() in desc.lower():
                if matched:
                    raise RuntimeError(f"❌ Conflict: '{desc}' matched both interest and unqualified div.")
                df.loc[idx, 'category'] = 'unqualified_div'
                matched = True
                print(f"⬜ {date} - {account} - {amount} - {desc} - unqualified_div ")
                break

        for sym in qualifiedDividendSymbols:
            if sym.lower() in desc.lower():
                if matched:
                    raise RuntimeError(f"❌ Conflict: '{desc}' matched multiple categories.")
                df.loc[idx, 'category'] = 'qualified_div'
                matched = True
                print(f"🟨 {date} - {account} - {amount} - {desc} - qualified_div ")
                break

        if not matched:
            print(f"❌ Investment income: {date} - {account} - {amount} - '{desc}' not classified.")

# Ensure all classified
for idx, row in df.iterrows():
    if "investment income" == str(row["category"]).lower():
        raise RuntimeError(f"❌ Unclassified dividend: '{str(row['description'])}'")

# Filter relevant
filtered = df[df['category'].isin(['qualified_div', 'unqualified_div', 'interest'])]

# Group + sum
summary = filtered.groupby(['account', 'category'])['amount'].sum().unstack(fill_value=0).reset_index()

# Taxable column
def compute_taxable(row):
    account = row['account']
    if 'IRA' not in account and 'HSA' not in account:
        return round(row.get('unqualified_div', 0) + row.get('interest', 0), 2)
    return 0.0

summary['taxable'] = summary.apply(compute_taxable, axis=1)

# Split into two tables
summary_hsa_ira = summary[summary['account'].str.contains("IRA|HSA", case=False, na=False)]
summary_other = summary[~summary['account'].str.contains("IRA|HSA", case=False, na=False)]

# Save both to Excel
with pd.ExcelWriter(output_excel_path, engine="xlsxwriter") as writer:
    summary_hsa_ira.to_excel(writer, sheet_name=tabNameTaxDeferred, index=False)
    summary_other.to_excel(writer, sheet_name=tabNameTaxable, index=False)

print(f"✅ Two tables saved to {output_excel_path}")

# Format with xlwings
wb = xw.Book(output_excel_path)

for sheet_name in [tabNameTaxDeferred, tabNameTaxable]:
    ws = wb.sheets[sheet_name]
    last_row = ws.range("A1").end("down").row
    last_col = ws.range("A1").end("right").column
    table_range = ws.range((1, 1), (last_row, last_col))

    table = ws.api.ListObjects.Add(1, table_range.api, 0, 1)
    table.Name = f"{sheet_name}Summary"
    table.TableStyle = "TableStyleMedium9"
    table.ShowTotals = True

    for i in range(2, 5):
        table.ListColumns(i).TotalsCalculation = constants.xlTotalsCalculationSum

    ws.autofit('columns')

wb.save()
print("✅ Both tables formatted with totals and styles.")
