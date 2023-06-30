import re

msg = "Thank you for using your Debit Card XX1581 for Rs.550 at KUNDAN LAL AND  NOIDA on 07-02-2019 10:19:51. Avl bal in A/C XX0117 is Rs.1035.27.Now get your account balance and much more on WhatsApp. Click kotak.com/wa to get started."

regex6 = r"Debit Card [A-Z]{2}\d{4} for (Rs\.|INR )(\d+).*"

match = re.search(regex6, msg, re.IGNORECASE)
if match:
    print(match.group(2))
regex_sender = r".*(swiggy|zomato|amazon|flipkart).*"
msg = "Instant Personal loans starting just at 1.5%. Borrow amounts from Rs 5000 to Rs 100000 from CASHe. Download CASHe and apply today!http://nsm.sg/VZy2h"
regex_loan1 = r"loan(?:.*?amount.*?)?\s*(?:Rs\.?|INR)\s*([\d,]+(?:\.\d{2})?)"
regex_loan2 = r"disbursed|processed|processing(?:\s+\w+)*?\s+loan.*?(?:Rs\.?|AMT|amount)\D*(\d+(?:\.\d+)?)"
regex_loan3 = r"loan .* disbursed"
if re.match(regex_loan3,msg,re.IGNORECASE): print("hello")