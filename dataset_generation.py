import random

import pandas as pd
from datetime import date, timedelta

actions = ["CREDITED", "RECEIVED", "DEBITED", "SALARY CREDIT", "EMI"]

additional_pre_texts = [

    "Transaction ID: 12345",

    "Payment received for Order #6789",

    "Deposit made via ATM",

    "Funds transferred from Account XYZ"

]

additional_post_texts = [
    "Thanks for banking with us",

    "Do not reply",

    "Contact customer support for help",

    "Not you?. Fwd this sms to 9264092640",

    "Transaction date is " + str(date.today())
]

dataset = []

# Generate 100 entries

for x in range(10400):
    action = random.choice(actions)

    additional_pre_text = random.choice(additional_pre_texts)
    additional_post_text = random.choice(additional_post_texts)

    account_number = str(random.randint(1000000000000001, 9999999999999999))

    amount = str(random.randint(100, 10000))

    message = f"{additional_pre_text} - {action} {account_number} with INR {amount}. {additional_post_text}"

    dataset.append(message)


df = pd.DataFrame(dataset, columns=["Message"])
df.to_excel("dataset.xlsx", index=False)

print("DONE")
