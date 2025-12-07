import pandas as pd
import xlwings as xw
import sys
import os
from win32com.client import constants

output_excel_path = "output.xlsx"

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
df['category'] = df['category'].str.strip().str.lower()

# Filter for relevant categories
filtered = df[df['category'].isin(['investment income', 'interest'])]

# Group and sum
summary = filtered.groupby(['account', 'category'])['amount'].sum().unstack(fill_value=0).reset_index()

# Add taxable column
def compute_taxable(row):
    account = row['account']
    if 'IRA' not in account and 'HSA' not in account:
        return round(row.get('investment income', 0) + row.get('interest', 0), 2)
    return 0.0

summary['taxable'] = summary.apply(compute_taxable, axis=1)

# Save to Excel first (without total row)
summary.to_excel(output_excel_path, index=False)

print("✅ Summary saved to output.xlsx")

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
table.ListColumns(4).TotalsCalculation = constants.xlTotalsCalculationSum

# Autofit all columns
ws.autofit('columns')

wb.save()
print("✅ Total row added with formulas and styled as a table.")