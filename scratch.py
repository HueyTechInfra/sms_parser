import json
import re
import openpyxl
import pandas as pd
import datetime

regex = r"(?i).*(?:credited|received|Credited|Received)\D*(INR|Rs.)\D*(\d+(?:\.\d+)?)"
regex1 = r"(?i).*(?:credited|received|Credited|Received)\D*(INR|Rs.)\D*(\d+(?:\.\d+)?)"
regex2 = r"(?i)(Rs.|INR)\D*(\d+(?:\.\d+)?).*(?:credited|received|Credited|Received)"
regex3 = r"(?i).*(Rs.|INR)\.*(\d+(?:\.\d+)?).*(?:credited|received|Credited|Received)"

# patters for debit messages:
regex4 = r"(?:Rs\.?\s*|INR)\s*(\d+(?:\.\d+)?)\s*(debited|withdrawn)"
regex5 = r"(?i)debited \D*(?:Rs\.|INR)?\s*(\d+(?:\.\d+)?)"

pattern_w = r"(?i).*(received|request|requested).*(received|request|requested)"
pattern_w1 = r"(?i).*(debited|debit)"

with open('data.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)
    for x in range(len(data)):
        data[x]["body"] = data[x]["body"].replace(",", "")
        data[x]["body"] = data[x]["body"].replace(",", "")

    count = 0
    count_mab = 0
    sum = 0
    str_temp = []
    account_no = []
    transaction_id = []
    amountcredited = []
    amountdebited = []
    amount = []
    category = []
    reason = []
    acc_bal = []
    date_mab = []
    workbook = openpyxl.load_workbook('complete_data.xlsx')
    sheet = workbook.active

    for x in range(len(data)):
        val = 0
        decline_bit = 0
        msg = data[x]["body"]
        if re.search(r".*EMI.*", msg, re.IGNORECASE):
            count += 1
            # msg contains the word EMI.
            # check if it is a reminder message
            if re.search(r"\b(?:pending|overdue|due|earliest|clear|presented)\b", msg, re.IGNORECASE):
                str_temp.append(msg)
                val = 1
                category.append("reminder")
                amountdebited.append(None)
                amountcredited.append(None)
                # if the msg contains amount to be paid
                if re.search(r"EMI.*?Rs\.?\s*([\d,.]+).*?(due|earliest)", msg):
                    match = re.search(r"EMI.*?Rs\.?\s*([\d,.]+).*?(due|earliest)", msg)
                    amount.append(float(match.group(1)))
                else:
                    amount.append(None)
            else:
                # emi debit msg
                match1 = re.search(regex4, msg, re.IGNORECASE)
                match2 = re.search(regex5, msg, re.IGNORECASE)

                if match1:
                    match = match1
                elif match2:
                    match = match2
                if (match1 or match2):
                    str_temp.append(msg)
                    val = 1
                    amountdebited.append(float(match.group(1)))
                    amountcredited.append(None)
                    amount.append(None)
                    category.append("EMI")
        elif re.match(pattern_w, msg):
            pass

        elif re.search(r'\b(declined|decline)[^a-zA-Z](.*?)[\.]', msg):
            val = 1
            decline_bit = 1
            str_temp.append(msg)
            category.append("decline")
            amountdebited.append(None)
            amountcredited.append(None)
            amount.append(None)
            match = re.search(r'\b(declined|decline)[^a-zA-Z](.*?)[\.]', msg)
            reason.append(match.group(2))

        elif re.match(regex1, msg):
            match = re.match(regex1, msg)
            sum += float(match.group(2))
            amountcredited.append(float(match.group(2)))
            category.append("credit")
            amountdebited.append(None)
            str_temp.append(msg)
            amount.append(None)
            count += 1
            val = 1
        elif re.match(regex2, msg):
            match = re.match(regex2, msg)
            sum += float(match.group(2))
            amountcredited.append(float(match.group(2)))
            category.append("credit")
            amountdebited.append(None)
            str_temp.append(msg)
            amount.append(None)
            count += 1
            val = 1
        elif re.match(regex3, msg) and (not re.match(pattern_w1, msg)):
            match = re.match(regex3, msg)
            sum += float(match.group(2))
            amountcredited.append(float(match.group(2)))
            category.append("credit")
            amountdebited.append(None)
            str_temp.append(msg)
            amount.append(None)
            count += 1
            val = 1

        elif re.search(r"\b(bounce)\b", msg, re.IGNORECASE):
            match = re.search(r"\b(bounce)\b", msg, re.IGNORECASE)
            val = 1
            amountdebited.append(None)
            amountcredited.append(None)
            str_temp.append(msg)
            category.append("Bounce")
            if re.search(r"(?:Rs|INR)\.?\s*([\d,.]+)", msg, re.IGNORECASE):
                match = re.search(r"(?:Rs|INR)\.?\s*([\d,.]+)", msg, re.IGNORECASE)
                amount.append(match.group(1))
            else:
                amount.append(None)

        elif re.search(regex4, msg):
            val = 1
            match = re.search(regex4, msg, re.IGNORECASE)
            amountdebited.append(float(match.group(1)))
            amountcredited.append(None)
            str_temp.append(msg)
            amount.append(None)
            count += 1
            category.append("debit")

        elif re.search(regex5, msg):
            match = re.search(regex5, msg, re.IGNORECASE)
            val = 1
            amountdebited.append(float(match.group(1)))
            amountcredited.append(None)
            str_temp.append(msg)
            amount.append(None)
            count += 1
            category.append("debit")

        if val == 1:
            pattern = r"(?i)(A/c no.|a/c no.|ac no.|AC no.|Ac no.)\D*(\d+(?:\.\d+)?).*"
            pattern1 = r"(?i)(A/c |a/c |ac |AC |Ac |account XXXXXXXX|Account XXXXXXXX|account ending with)\D*(\d+(?:\.\d+)?).*"
            pattern2 = r"(?i)(ef | Ref | Reference |txn |Txn )\D*(\d+(?:\.\d+)?).*"
            pattern3 = r"Ref\.No:(\d+)"  # to match the Ref No
            pattern4 = r"IMPS/P2A/(\d+)/(\d+)(?:/remar)?"  # to match the IMPS/P2A value
            pattern5 = r"NEFT.*?(\d+)"  # to extarct NEFT
            pattern6 = r"UPI/(?:CRADJ|P2A)/([^/]+)"  # to extract UPI
            pattern7 = r"Info\D*(\d{6,})"  # to extract Info
            match1 = re.search(pattern, msg)
            match2 = re.search(pattern1, msg)
            match3 = re.search(pattern2, msg)
            match4 = re.search(pattern3, msg)
            match5 = re.search(pattern4, msg)
            match6 = re.search(pattern5, msg, re.IGNORECASE)
            match7 = re.search(pattern6, msg)
            match8 = re.search(pattern7, msg)
            if decline_bit == 0: reason.append(None)

            if match1:
                account_no.append(match1.group(2))
            elif match2:
                account_no.append(match2.group(2))
            else:
                account_no.append(None)

            if match3:
                transaction_id.append(match3.group(2))
            elif match4:
                transaction_id.append(match4.group(1))
            elif match5:
                transaction_id.append(match5.group(1) + "/" + match5.group(2))
            elif match6:
                transaction_id.append(match6.group(1))
            elif match7:
                transaction_id.append(match7.group(1))
            elif match8:
                transaction_id.append(match8.group(1))
            else:
                transaction_id.append(None)

            match1 = re.search(r'\b(balance|bal|bal ).*(Rs.|INR |Rs. |INR)(\d+)', msg)
            match2 = re.search(r'\b(balance|bal|bal ).*(Rs. -|INR -)(\d+)', msg)

            if match1:
                acc_bal.append(float(match1.group(3)))
            elif match2:
                acc_bal.append(int(match2.group(3)) * (-1))
            else:
                acc_bal.append(None)
        if bool(re.search(r'\b(mab)\b', msg, re.IGNORECASE)):
            count_mab += 1
            s_time1 = re.sub("\D", '', "/Date(" + str(data[x]["date"]) + ")/")
            d_time1 = datetime.datetime.fromtimestamp(float(s_time1) / 1000).strftime('%Y-%m-%d')
            date_mab.append(d_time1)
    print(count_mab)
    print(date_mab)
    # Create a new DataFrame with messages and amounts debited
    new_df = pd.DataFrame({'Message': str_temp, 'Amount Debited': amountdebited, 'Amount Credited': amountcredited,
                           'account number': account_no, 'transaction id': transaction_id, "Amount": amount,
                           "category": category, "reason": reason, "account balance": acc_bal})
    # Save the new DataFrame to a new Excel file
    new_df.to_excel('messages_with_amountsV2.xlsx', index=False)
    # print(str_temp)
json_file.close()
workbook.save('complete_data.xlsx')
