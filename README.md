EstimateIRSTax

A lightweight tool for estimating taxable investment income.
Currently designed to run on Windows 11.

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

