import csv
import random
import hashlib
import sys
import os

# Check for input argument
if len(sys.argv) < 2:
    print("Usage: python anonymize_transactions.py <input_file.csv>")
    sys.exit(1)

input_file = sys.argv[1]

# Validate file existence
if not os.path.isfile(input_file):
    print(f"Error: File '{input_file}' not found.")
    sys.exit(1)

# Generate output filename
base_name = os.path.splitext(os.path.basename(input_file))[0]
# Ensure results folder exists
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)
 # Build output path
output_file = os.path.join(results_dir, f"{base_name}_anonymized.csv")

# Generate a consistent fake name for each account
def anonymize_account(account_name):
    seed = hashlib.md5(account_name.encode()).hexdigest()
    random.seed(seed)
    adjectives = ["Blue", "Shiny", "Calm", "Beautiful", "Smart", "Strong", "Brave", "Happy"]
    nouns = ["Kitten", "Puppy", "Fire", "Ocean", "Avocado", "Lemon", "Lavendar", "Mist"]

    # Preserve IRA/HSA if present in the original account name
    suffix = ""
    if "IRA" in account_name.upper():
        suffix = "IRA"
    elif "HSA" in account_name.upper():
        suffix = "HSA"
    else:
        suffix = str(random.randint(1000, 9999))

    return f"{random.choice(adjectives)} {random.choice(nouns)} {suffix}"

# Randomize amount while preserving sign
def randomize_amount(original_amount):
    try:
        amount = float(original_amount)
        sign = -1 if amount < 0 else 1
        rng = random.Random()  # Create a local random generator
        new_amount = round(rng.uniform(0, 2000), 2)
        return str(sign * new_amount)
    except:
        return original_amount  # If it's not a number, leave it as-is

# Process the file
input_count = 0
output_count = 0

with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        input_count += 1
        row['Account'] = anonymize_account(row['Account'])
        row['Amount'] = randomize_amount(row['Amount'])
        row.pop('Tags', None)  # Safely remove 'Tags' if it exists
        writer.writerow(row)
        output_count += 1

print(f"✅ Anonymized file saved as: {output_file}")
print(f"📊 Rows processed: Input = {input_count}, Output = {output_count}")
