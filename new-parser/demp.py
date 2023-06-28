import re

msg = "Thank you for using your Debit Card XX1581 for Rs.550 at KUNDAN LAL AND  NOIDA on 07-02-2019 10:19:51. Avl bal in A/C XX0117 is Rs.1035.27.Now get your account balance and much more on WhatsApp. Click kotak.com/wa to get started."

regex6 = r"Debit Card [A-Z]{2}\d{4} for (Rs\.|INR )(\d+).*"

match = re.search(regex6, msg, re.IGNORECASE)
if match:
    print(match.group(2))

