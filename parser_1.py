import json
import re
import openpyxl
import pandas as pd

regex = r"(?i).*(?:credited|received|Credited|Received)\D*(INR|Rs.)\D*(\d+(?:\.\d+)?)"
regex1 = r"(?i).*(?:credited|received|Credited|Received)\D*(INR|Rs.)\D*(\d+(?:\.\d+)?)"
regex2 = r"(?i)(Rs.|INR)\D*(\d+(?:\.\d+)?).*(?:credited|received|Credited|Received)"
regex3 = r"(?i).*(Rs.|INR)\.*(\d+(?:\.\d+)?).*(?:credited|received|Credited|Received)"
pattern_w = r"(?i).*(received|request|requested).*(received|request|requested)"
pattern_w1 = r"(?i).*(debited|debit)"
msg = "Your AC XXXXX291184 Credited INR 11.35 on 30/09/18 -MAB SB Debit . Avl Bal INR 0.00.Plz download Buddy"
print(bool(re.match(regex1,msg)))
print(bool(re.match(regex2,msg)))
print(bool(re.match(regex3,msg)))
with open('data.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)
    for x in range(len(data)): data[x]["body"] = data[x]["body"].replace(",", "")
    count = count_ac = sum = count_penalty = 0
    str_temp = account_no = transaction_id = amount = []
    workbook = openpyxl.load_workbook('complete_data.xlsx')
    sheet = workbook.active
    for x in range(len(data)):
        val = 0  # categorizing the credit message to decide to find transaction id and account number or not
        msg = data[x]["body"]
        if re.match(pattern_w, msg):  # for removing messages containing both words "request" and "received"
            pass
        elif re.match(regex1, msg):
            match = re.match(regex1, msg)
            sum += float(match.group(2))
            amount.append(float(match.group(2)))
            str_temp.append(msg)
            count += 1
            val = 1
        elif re.match(regex2, msg):
            match = re.match(regex2, msg)
            sum += float(match.group(2))
            amount.append(float(match.group(2)))
            str_temp.append(msg)
            count += 1
            val = 1
        elif re.match(regex3, msg) and (not re.match(pattern_w1, msg)):
            match = re.match(regex3, msg)
            sum += float(match.group(2))
            amount.append(float(match.group(2)))
            str_temp.append(msg)
            count += 1
            val = 1
        # categorizing overdue msgs and fetching dates or payment reference number present in the sms
        elif re.search(r'\boverdue\b', msg) and not re.search(r'\bEMI\b', msg):
            match = re.search(r'\b(\d+).*(overdue)\b', msg)
            match1 = re.search(r'\b(overdue)\D+(\d+)\b', msg)
            match2 = re.search(r'\b(overdue)\D+(\d{1,2}\.\d{1,2}\.\d{2,4})\b', msg)
            # if match2:
            #     print(match2.group(2))
            # elif match:
            #     print(match.group(1))
            # elif match1:
            #     print(match1.group(2))
        # elif re.search(r'\b(declined|decline)[^a-zA-Z](.*?)[\.]', msg):
        #     match = re.search(r'\b(declined|decline)[^a-zA-Z](.*?)[\.]', msg)
        #     print("reason : ", match.group(2))
        #     match1 = re.search(r'\b(balance|bal).*(Rs.|INR )(\d+)', msg)
        #     match2 = re.search(r'\b(balance|bal).*(Rs. -|INR -)(\d+)', msg)
        #     match3 = re.search(r'\b\D+(\d)(\w+).*(declined|decline).*', msg)
        #     if (match1):
        #         print("amount : ", match1.group(3))
        #     elif (match2):
        #         print("amount : ", int(match2.group(3)) * (-1))
        #     elif match3:
        #         print("number : ", match3.group(1) + match3.group(2))
        # elif re.search(r'\b(MAB|mab)\b', msg):
        #     val = 1
        #     count_penalty += 1
        #     print(msg)
        if val == 1:
            pattern = r"(?i)(A/c no.|a/c no.|ac no.|AC no.|Ac no.)\D*(\d+(?:\.\d+)?).*"
            pattern1 = r"(?i)(A/c |a/c |ac |AC |Ac |account XXXXXXXX|Account XXXXXXXX|account ending with)\D*(\d+(?:\.\d+)?).*"
            pattern2 = r"(?i)(ref|Ref|Reference |txn |Txn )\D*(\d+(?:\.\d+)?).*"
            pattern_date = r'\d{1,2}[/|.]\d{1,2}[/|.]\d{2,4}'  # finding date from sms
            pattern_bal = r'\b(balance|bal).*(Rs. |INR |Rs.|INR)(\d+)'
            match1 = re.search(pattern, msg)
            match2 = re.search(pattern1, msg)
            match3 = re.search(pattern2, msg)
            match4 = re.search(pattern_date, msg)
            match5 = re.search(pattern_bal, msg, re.IGNORECASE)
            # for fetching account numbers
            if match1:
                count_ac += 1
                account_no.append(match1.group(2))
            elif match2:
                account_no.append(match2.group(2))
                count_ac += 1
            else:
                account_no.append(None)

            # for fetching transaction ids
            if re.match(r'.*(refund|Refund|REFUND|REFERRAL).*\d{1,2}\.\d{1,2}\.\d{2,4}', msg):
                transaction_id.append(None)
            elif match3:
                transaction_id.append(match3.group(2))
                count_ac += 1
            else:
                transaction_id.append(None)
            if match5:
                print(msg)
                print(match5.group(3))
    print(count_penalty)
    print(sum)
    # Create a new DataFrame with messages amounts credited/debited, account number and transaction/reference id
    new_df = pd.DataFrame(
        {'Message': str_temp, 'Amount Credited': amount, 'account number': account_no,
         'transaction id': transaction_id})

    # Save the new DataFrame to a new Excel file
    new_df.to_excel('output.xlsx', index=False)
json_file.close()
workbook.save('complete_data.xlsx')
