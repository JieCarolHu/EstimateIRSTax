EstimateIRSTax

A lightweight tool for estimating taxable investment income, this project is designed to quickly calculate taxable amounts from annual transaction data. I use Empower, formerly known as Personal Capital, to manage all of my bank, investment, and credit card accounts. From there, I export a full year of transactions as a CSV file to serve as the input for the tool.

The script loads this raw CSV and automatically filters out relevant entries, focusing on transactions categorized as interest and investment income. It then further distinguishes investment income between qualified dividends and unqualified dividends, ensuring that only interest and unqualified dividends are included in the taxable income summary. Qualified dividends are identified separately but excluded from the taxable calculation.

The result is a clear and consolidated view of taxable amounts, broken down by account and type of income. The summary includes interest, qualified dividends, and unqualified dividends, making it easier to prepare for tax reporting and understand the composition of investment income across accounts. Accounts such as HSA and IRA are still listed in the output Excel file for completeness, but they are excluded from the total taxable calculation since they are tax‑advantaged.

--------------------------------------------------
src/anonymize_transactions.py
--------------------------------------------------

Usage:
    python .\src\anonymize_transactions.py ".\examples\2025-01-01 thru 2025-12-07 transactions.csv"

Input:
    Raw transaction files (CSV format), typically downloaded from Empower (formerly Personal Capital).
    Expected columns: Date, Account, Description, Category, Tags, Amount

Output:
    results/xxxx_anonymized.csv

Functionality:
    - Generates anonymized versions of your transaction data for safe debugging and sharing
    - Account names replaced with randomized but consistent pseudonyms
    - Preserves IRA or HSA labels if they already exist in the original account name
    - Transaction amounts randomized while preserving sign (income vs. expense)

--------------------------------------------------
src/calcTaxableInvestIncome.py
--------------------------------------------------

Usage:
    python .\src\calcTaxableInvestIncome.py ".\examples\2025-01-01 thru 2025-12-07 transactions.csv"

Input:
    Transaction file (raw or anonymized)

Output:
    results/output.xlsx

Functionality:
    - Loads and normalizes transaction data
    - Filters for relevant categories (investment income, interest)
    - Groups transactions by account and category, then calculates totals
    - Adds a Taxable column:
        * Accounts not marked as IRA/HSA are included in taxable totals
        * IRA/HSA accounts are excluded
    - Saves results to Excel (output.xlsx)
    - Formats the sheet as a styled table with a totals row
    - Automatically adds a sum formula for the taxable column
    - Autofits columns for readability

--------------------------------------------------
Notes
--------------------------------------------------

- Designed for personal use and quick tax estimation
- Anonymization helps with debugging and sharing without exposing sensitive data
- Future versions may expand compatibility beyond Windows 11


