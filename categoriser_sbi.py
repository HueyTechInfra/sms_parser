import pickle
import re
import pandas as pd
from parse import *
from datetime import datetime

# patters for credit messages:
regex = r"(?i).*(?:credited|received|Credited|Received|deposited)\D*(INR|Rs.)\D*(\d+(?:\.\d+)?)"
regex1 = r"(?i).*(?:credited|received|Credited|Received|deposited)\D*(Rs.|INR|Rs. |INR )(\d+(?:\.\d+)?)"
regex2 = r"(?i)(Rs.|INR)\D*(\d+(?:\.\d+)?).*(?:credited|received|Credited|Received|deposited)"
regex3 = r"(?i).*(Rs.|INR)\.*(\d+(?:\.\d+)?).*(?:credited|received|Credited|Received|deposited)"
pattern_temp2 = "Your A/C {} has a credit by Transfer of Rs {amount} {}"  # sbi special

# patters for debit messages:
regex4 = r"(Rs.|INR|Rs. |INR )(\d+(?:\.\d+)?).*(debited|withdrawn)"
regex5 = r"(?i).*(?:debited|paying|withdrawn)\D*(Rs.|INR|Rs. |INR )(\d+(?:\.\d+)?)"
regex6 = r"Debit Card .* for .* (Rs\.*|INR )(\d+).*"
regex7 = r".*(Rs\.|INR)(\d+\.*\d+)\s*was spent (.*) Card"
pattern_temp = "Your a/c no. {} is debited for Rs.{amount} {} a/c {} credited {}"
pattern_temp1 = "Your a/c no. {} is debited Rs.{amount} {} a/c {} credited {}"
pattern_temp3 = "{}State Bank Internet Banking{} transaction of Rs. {amount} {}"  # sbi special for internet banking transactions

# pattern for ambiguous sms
pattern_w = r"(?i).*(received|request|requested).*(received|request|requested)"
pattern_w1 = r"(?i).*(debited|debit)"
pattern_w2 = r".*(congratulations|congrats|true|order placed|myntra|lenskart).*"
pattern_w3 = r"\b(?:pending|overdue|due|earliest|clear|presented|reminder|scheduled)\b"

# pattern for utility messages
regex_util1 = r"(?i)(?:Debited|Credited)\s*(?:\S+\s+)?(?:INR|Rs\.?|Rs)\s*([\d,.]+).*?recharge"
regex_util2 = r"Recharge done\s*.*?MRP:\s*(?:INR|Rs\.?|Rs)([\d,.]+)"
regex_util3 = r"(?:Rs\.?|INR)\s?([\d,.]+)\s*recharge successful"
regex_util4 = r"(?i)recharge.*?\b(?:Rs\.?|INR)\s*([\d,.]+)\b.*?successful"

format = "%Y-%m-%d"  # used for extraction human-readable date from json date format

# regex for loan amounts
regex_loan1 = r"loan(?:.*?amount.*?)?\s*(?:Rs\.?|INR)\s*([\d,]+(?:\.\d{2})?)"
regex_loan2 = r"disbursed|processed|processing(?:\s+\w+)*?\s+loan.*?(?:Rs\.?|AMT|amount)\D*(\d+(?:\.\d+)?)"
regex_loan3 = r"loan .* disbursed"

# regex to count swiggy/zomato/amazon messages
regex_sender = r".*(swiggy|zomato|amazon|flipkart|snapdeal|foodpanda).*"
regex_otp1 = r".*(\d+) is (the|your)* (otp|one time security code|one time password)"
regex_otp2 = r".*(otp|one time password|one time security code) .* is (\d+)"

regex_promotion = r".*(congrats|congratulations|winner|lucky|win big|discount|cashback|happy).*"
regex_auto_debit = r".*(auto-debit|auto debit|e-mandate|mandate).*(request|requested|approved|registration)"
str_temp = []
category = []
date = []
sender = []
length = []
primary_type = []
sub_category = []
amount = []
account_no = []
transaction_id = []
acc_bal = []
len_sms = []
sender_all = []


def categoriser(data):
    for x in range(len(data)):
        try:
            sender = (data[x]['address'])
        except:
            try:
                sender = (data[x]["address"])
            except:
                sender = None
        try:
            msg = (data[x]['body'])
        except:
            try:
                msg = (data[x]["body"])
            except:
                msg = None
                break
        msg = msg.replace(",", "")  # removing comma to read the amount in full form
        s_time1 = re.sub("\D", '', "/Date(" + str(data[x]["date"]) + ")/")
        d1 = datetime.fromtimestamp(float(s_time1) / 1000).strftime('%Y-%m-%d')
        d = datetime.strptime(d1, format)
        date.append(d)
        str_temp.append(msg)
        len_sms.append(len(msg))
        sender_all.append(sender)

        # sbi special credit card bill paid sms
        if re.match(r".*payment of Rs. (\d+\.*\d+) .* Credit Card .* processed", msg, re.IGNORECASE):
            match = re.match(r".*payment of Rs. (\d+\.*\d+) .* Credit Card .* processed", msg, re.IGNORECASE)
            amount.append(float(match.group(1)))
            primary_type.append("transaction")
            sub_category.append("cc payment")

        # loan disbursed
        elif re.search(regex_loan1, msg, re.IGNORECASE) or re.search(regex_loan2, msg, re.IGNORECASE):
            if re.search(regex_loan1, msg, re.IGNORECASE):
                match = re.search(regex_loan1, msg, re.IGNORECASE)
            else:
                match = re.search(regex_loan2, msg, re.IGNORECASE)
            amount.append(match.group(1))
            primary_type.append("info")
            sub_category.append("loan")
        elif re.search(regex_loan3, msg, re.IGNORECASE):
            if re.search(r"(Rs.|INR).*(\d+)", msg, re.IGNORECASE):
                match = re.search(r"(Rs.|INR).*(\d+)", msg, re.IGNORECASE)
                amount.append(match.group(1))
            else:
                amount.append(None)
            primary_type.append("info")
            sub_category.append("loan")

        # finding promotional/advertisement messages
        elif re.search(regex_promotion, msg, re.IGNORECASE):
            if (re.match(r".* credit card application", msg, re.IGNORECASE)):
                primary_type.append("info")
            else:
                primary_type.append("promotion")
            sub_category.append(None)
            amount.append(None)

        # finding emi msgs
        elif re.search(r".*EMI.*", msg, re.IGNORECASE):
            sub_category.append("emi")
            # check if it is a reminder message
            if re.search(pattern_w3, msg, re.IGNORECASE) or re.search(r".* will be debited", msg, re.IGNORECASE):
                primary_type.append("info")
                # if the msg contains amount to be paid
                if re.search(r"EMI.*?Rs\.?\s*(\d+\.\d+).*?(due|earliest)", msg):
                    match = re.search(r"EMI.*?Rs\.?\s*(\d+\.\d+).*?(due|earliest)", msg)
                    try:
                        amount.append(float(match.group(1)))
                    except:
                        amount.append(int(match.group(1)))
                elif re.search(r".*EMI due on .*(Rs|INR) (\d+) .*", msg, re.IGNORECASE):
                    match = re.search(r".*EMI due on .*(Rs|INR) (\d+) .*", msg, re.IGNORECASE)
                    try:
                        amount.append(float(match.group(2)))
                    except:
                        amount.append(int(match.group(2)))
                else:
                    amount.append(None)
            # emi debit msg
            else:
                primary_type.append("transaction")
                match1 = re.search(regex4, msg, re.IGNORECASE)
                match2 = re.search(regex5, msg, re.IGNORECASE)
                if match1:
                    amount.append(float(match1.group(2)))
                elif match2:
                    amount.append(float(match2.group(2)))
                else:
                    amount.append(None)

        elif re.match(pattern_w, msg) or re.match(pattern_w3, msg, re.IGNORECASE) or re.search(r".* will be debited",
                                                                                               msg, re.IGNORECASE):
            primary_type.append("info")
            sub_category.append(None)
            amount.append(None)

        # finding otp msgs
        elif re.search(regex_otp1, msg, re.IGNORECASE) or re.search(regex_otp2, msg, re.IGNORECASE):
            if re.search(regex_otp1, msg, re.IGNORECASE):
                match = re.search(regex_otp1, msg, re.IGNORECASE)
            else:
                match = re.search(regex_otp2, msg, re.IGNORECASE)
            primary_type.append("otp")
            amount.append(None)
            sub_category.append("otp")

        # finding standing instructions
        elif re.search(regex_auto_debit, msg, re.IGNORECASE) or re.match(r".* standing instruction", msg,
                                                                         re.IGNORECASE):
            primary_type.append("info")
            sub_category.append("standing instruction")
            if re.match(r"(rs.|INR).*(\d+)", msg, re.IGNORECASE):
                match = re.match(r"(rs.|INR).*(\d+)", msg, re.IGNORECASE)
                amount.append(match.group(1))
            else:
                amount.append(None)

        elif parse(pattern_temp, msg) or parse(pattern_temp1, msg) or parse(pattern_temp3, msg):
            if parse(pattern_temp, msg):
                amount.append(float(parse(pattern_temp, msg)['amount']))
            elif parse(pattern_temp3, msg):
                amount.append(float(parse(pattern_temp3, msg)['amount']))
            else:
                amount.append(float(parse(pattern_temp1, msg)['amount']))
            primary_type.append("transaction")
            sub_category.append("debit")


        # finding credit msgs
        elif re.match(regex1, msg, re.IGNORECASE) and not re.search(pattern_w3, msg, re.IGNORECASE) and not re.search(
                pattern_w2, msg, re.IGNORECASE):
            match = re.match(regex1, msg)
            primary_type.append("transaction")
            amount.append(float(match.group(2)))
            sub_category.append("credit")

        elif re.search(regex2, msg, re.IGNORECASE) and not re.search(pattern_w3, msg, re.IGNORECASE) and not re.search(
                pattern_w2, msg, re.IGNORECASE):
            match = re.search(regex2, msg, re.IGNORECASE)
            primary_type.append("transaction")
            if re.match(r".* salary", msg, re.IGNORECASE):
                sub_category.append("salary")
            else:
                sub_category.append("credit")
            amount.append(float(match.group(2)))

        # special case of credit messages are dealt here where those sms aren't categorized which are actually debit sms
        # but provide information of account getting credited
        elif re.match(regex3, msg) and (not re.match(pattern_w1, msg)) and not re.search(
                pattern_w2, msg, re.IGNORECASE) and not re.search(pattern_w3, msg, re.IGNORECASE):
            match = re.match(regex3, msg)
            primary_type.append("transaction")
            amount.append(float(match.group(2)))
            if re.match(r".* salary", msg, re.IGNORECASE):
                sub_category.append("salary")
            else:
                sub_category.append("credit")

        elif parse(pattern_temp2, msg):
            amount.append(float(parse(pattern_temp2, msg)['amount']))
            primary_type.append("transaction")
            sub_category.append("credit")

        # finding debit msgs
        elif re.search(regex4, msg) or re.search(regex6, msg) or re.search(regex7, msg, re.IGNORECASE):
            if re.search(regex6, msg):
                match = re.search(regex6, msg)
            elif re.search(regex7, msg, re.IGNORECASE):
                match = re.search(regex7, msg, re.IGNORECASE)
            else:
                match = re.search(regex4, msg, re.IGNORECASE)
            amount.append(float(match.group(2)))
            primary_type.append("transaction")
            sub_category.append("debit")

        elif re.search(regex5, msg):
            match = re.search(regex5, msg)
            amount.append(float(match.group(2)))
            primary_type.append("transaction")
            sub_category.append("debit")

        elif re.match(r'.*(legal notice)', msg, re.IGNORECASE):
            primary_type.append("info")
            amount.append(None)
            sub_category.append("legal notice")

        # finding occurrences of declined payments
        elif re.search(r'\b(declined|decline)[^a-zA-Z](.*?)[\.]', msg):
            primary_type.append("info")
            amount.append(None)
            match = re.search(r'\b(declined|decline)[^a-zA-Z](.*?)[\.]', msg)
            sub_category.append(match.group(2))

        elif re.search(r"\b(bounce)\b", msg, re.IGNORECASE):
            primary_type.append("transaction")
            sub_category.append("Bounce")
            if re.search(r"(?:Rs|INR)\.?\s*([\d,.]+)", msg, re.IGNORECASE):
                match = re.search(r"(?:Rs|INR)\.?\s*([\d,.]+)", msg, re.IGNORECASE)
                amount.append(match.group(1))
            else:
                amount.append(None)

        # finding utility sms
        elif re.search(regex_util1, msg) or re.search(regex_util2, msg) or re.search(regex_util3, msg) or re.search(
                regex_util4, msg):
            if re.search(regex_util1, msg):
                match = re.search(regex_util1, msg)
            elif re.search(regex_util2, msg):
                match = re.search(regex_util2, msg)
            elif re.search(regex_util3, msg):
                match = re.search(regex_util3, msg)
            elif re.search(regex_util4, msg):
                match = re.search(regex_util4, msg)
            primary_type.append("transaction")
            sub_category.append("utility")
            amount.append(float(match.group(1).replace(',', '')))

        # cheque returned
        elif re.search(r'(cheque).*(returned)', msg, re.IGNORECASE):
            primary_type.append("info")
            sub_category.append("cheque returned")
            amount.append(None)

        # e-commerce
        elif re.search(regex_sender, sender, re.IGNORECASE) and re.search(
                r"(order|placed|delivered|ordered|arriving|arrived|return)", msg,
                re.IGNORECASE):
            primary_type.append("info")
            sub_category.append("e-commerce")
            if re.search(r"(Rs.|INR|Rs. |INR )(\d+(?:\.\d+)?)", msg, re.IGNORECASE):
                match = re.search(r"(Rs.|INR|Rs. |INR )(\d+(?:\.\d+)?)", msg, re.IGNORECASE)
                amount.append(match.group(2))
            else:
                amount.append(None)

        # finding mab occurrences or exceeded card limits
        elif re.search(r'\b(mab)\b', msg, re.IGNORECASE) or re.search(r".*(exceeded).*(credit limit).*", msg,
                                                                      re.IGNORECASE):
            primary_type.append("info")
            if re.search(r'\b(mab)\b', msg, re.IGNORECASE):
                sub_category.append("mab")
            else:
                sub_category.append("exceeded credit card limit")
            amount.append(None)


        # categorising rest of the sms as others
        else:
            primary_type.append("others")
            sub_category.append(None)
            amount.append(None)

        # finding account_number, transaction_id and account_balance

        pattern = r"(?i)(A/c no.|a/c no.|ac no.|AC no.|Ac no.)\D*(\d+(?:\.\d+)?).*"
        pattern1 = r".*(A/c |A/c|A/C|A/C |a/c |ac |AC |Ac |account |Account |account ending with |A/c ending )(\d+)"
        pattern2 = r"(?i)(ef | Ref | Reference |txn |Txn )\D*(\d+(?:\.\d+)?).*"

        # regex to find transaction ids/reference numbers
        pattern3 = r"Ref\.No:(\d+)"  # to match the Ref No
        pattern4 = r"IMPS/\D+/(\d+)/(\d+)"  # to match the IMPS/P2A value
        neft = r".*NEFT"  # to extract NEFT
        pattern6 = r"UPI/(?:CRADJ|P2A)/([^/]+)"  # to extract UPI
        pattern7 = r"Info\D*(\d{6,})"  # to extract Info

        # regex for card transactions
        pattern8 = r"(?i)(?:Rs\.?|INR)\s*([\d,]+\.\d+|\d+(?:,\d+)?)\b.*?\bdebited\b.*?\bcard\b"
        # regex for atm transactions
        pattern9 = r"(?i)(?:Rs\.?|INR)\s*(?:\S+\s+)?([\d,.]+).*?withdrawn.*?(?:\s+\S+)?\s+atm"
        pattern10 = r"(?i)Debited\s*(?:\S+\s+)?(?:Rs\.?|INR)\s*(?:\S+\s+)?([\d,.]+).*?CASH-ATM"

        match1 = re.search(pattern, msg, re.IGNORECASE)
        match2 = re.search(pattern1, msg, re.IGNORECASE)
        match3 = re.search(pattern2, msg, re.IGNORECASE)
        match4 = re.search(pattern3, msg, re.IGNORECASE)
        match5 = re.search(pattern4, msg, re.IGNORECASE)
        match6 = re.search(neft, msg, re.IGNORECASE)
        match7 = re.search(pattern6, msg, re.IGNORECASE)
        match8 = re.search(pattern7, msg, re.IGNORECASE)
        # match9 = re.search(pattern8, msg, re.IGNORECASE)
        # match10 = re.search(pattern9, msg, re.IGNORECASE)
        # match11 = re.search(pattern10, msg, re.IGNORECASE)

        if match1:
            account_no.append(int(match1.group(2)[-4:]))
        elif match2:
            account_no.append(str(match2.group(2)[-4:]))
        else:
            account_no.append(None)

        # fetching transaction ids/reference numbers
        if match3:
            transaction_id.append(match3.group(2))
        elif match4:
            transaction_id.append(match4.group(1))
        elif match5:
            transaction_id.append(match5.group(1) + "/" + match5.group(2))
        elif match6:
            pattern = r"NEFT/(\w+)/(\D+)\."
            pattern1 = r"UTR (\w+) by (\D+)"
            match = re.search(pattern, msg, re.IGNORECASE)
            match1 = re.search(pattern1, msg, re.IGNORECASE)
            if match:
                transaction_id.append(match.group(1) + "/" + match.group(2))
            elif match1:
                transaction_id.append(match1.group(1) + "/" + match1.group(2))
            else:
                transaction_id.append(None)

        elif match7:
            transaction_id.append(match7.group(1))
        elif match8:
            transaction_id.append(match8.group(1))
        else:
            transaction_id.append(None)

        match1 = re.search(r'\b(balance|bal|bal |credit limit:).*(Rs.|INR |Rs. |INR)(\d+)', msg,
                           re.IGNORECASE)  # credit limit is added specially for sbi bank
        match2 = re.search(r'\b(balance|bal|bal ).*(Rs. -|INR -)(\d+)', msg, re.IGNORECASE)

        # finding account balance from sms
        if match1:
            acc_bal.append(float(match1.group(3)))
        elif match2:
            acc_bal.append(int(match2.group(3)) * (-1))
        else:
            acc_bal.append(None)

        # finding category of msg : bank, upi, wallet, fastag, e-commerce
        if re.search(regex_sender, sender, re.IGNORECASE):
            if sub_category[-1] == "e-commerce":
                category.append("e-commerce")
            else:
                category.append("others")
        elif match7:
            category.append("UPI")
        elif re.search(r"(hdfc|pnb|bank|bnk|axis|idfc|kotak|sbi)", sender, re.IGNORECASE):
            category.append("bank")
        elif primary_type[-1] == "transaction" and re.match(r"wallet", msg, re.IGNORECASE):
            category.append("wallet")
        elif re.match("fastag", msg, re.IGNORECASE):
            category.append("fastag")
        else:
            category.append("others")
    new_df = pd.DataFrame(
        {'Message': str_temp, 'Sender': sender_all, 'Account Number': account_no, 'Transaction ID': transaction_id,
         "Amount": amount,
         "primary type": primary_type, "Category": category, "sub category": sub_category, "Account Balance": acc_bal,
         "Date": date, "Length_SMS": len_sms})

    # Save the new DataFrame to a new Excel file
    new_df.to_excel('output.xlsx', index=False)


a = 0
b = 100
with open(f'sms_dump_{a}_{b}.pkl', 'rb') as f:
    data = pickle.load(f)
    categoriser(data)
f.close()

# code to find if there is amount that is being self transferred to falsely increase credibility
primary_type.reverse()
sub_category.reverse()
account_no.reverse()
date.reverse()
amount.reverse()

amt = 0
for x in range(len(primary_type)):
    if primary_type[x] == "transaction" and sub_category[x] == "debit" and account_no[x] is not None:
        y = x + 1  # iterating through transactions after x transaction on that date
        while y < len(primary_type) and date[y] == date[x]:
            if sub_category[y] == "credit":
                if account_no[y] is not None and account_no[y] != account_no[x] and amount[y] == amount[x]:
                    amt += amount[x]
                    break
            y += 1

amt_new = 0
for x in range(len(primary_type)):
    if primary_type[x] == "transaction" and sub_category[x] == "credit" and account_no[x] is not None:
        y = x + 1  # iterating through transactions after x transaction on that date
        while y < len(primary_type) and date[y] == date[x]:
            if sub_category[y] == "debit":
                if account_no[y] is not None and account_no[y] != account_no[x] and amount[y] == amount[x]:
                    amt_new += amount[x]
                    break
            y += 1

print("total self transfer amounts are :", amt_new, amt)
