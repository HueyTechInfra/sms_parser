import pandas as pd

# Load the Excel file
df = pd.read_excel('messages_with_amountsV2.xlsx')

# Get the columns for amount and date
amount_column = 'Amount Credited'
date_column = 'Date'

# Initialize variables for tracking pattern
pattern_day = 30
buffer = 5000

# Initialize variables for tracking maximum amount
max_amount = None
max_amount_date = None

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    # Get the amount and date from the respective columns
    amount = row[amount_column]
    date = row[date_column]

    # Check if the amount and date are not NaN
    if pd.notnull(amount) and pd.notnull(date):
        # Check if the date matches the pattern day or the +/- 1 days
        if date.day in [pattern_day, pattern_day - 1, pattern_day - 2, pattern_day + 1, pattern_day + 2]:
            # Check if the amount falls within the buffer range
            if max_amount is None or amount > max_amount:
                max_amount = amount
                max_amount_date = date

# Check if a maximum amount was found
if max_amount is not None:
    print("Maximum amount found under the pattern:")
    print("Amount: ${:.2f}".format(max_amount))
    print("Date: {}".format(max_amount_date.strftime("%Y-%m-%d")))
else:
    print("No amount found under the pattern for the given date.")