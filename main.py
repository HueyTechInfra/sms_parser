import json
import re
import openpyxl
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import parser_1 as parser

# patters for credit messages:
regex = r"(?i).*(?:credited|received|Credited|Received)\D*(INR|Rs.)\D*(\d+(?:\.\d+)?)"
regex1 = r"(?i).*(?:credited|received|Credited|Received)\D*(INR|Rs.)\D*(\d+(?:\.\d+)?)"
regex2 = r"(?i)(Rs.|INR)\D*(\d+(?:\.\d+)?).*(?:credited|received|Credited|Received)"
regex3 = r"(?i).*(Rs.|INR)\.*(\d+(?:\.\d+)?).*(?:credited|received|Credited|Received)"

# patters for debit messages:
regex4 = r"(?:Rs\.?\s*|INR)\s*(\d+(?:\.\d+)?)\s*(debited|withdrawn)"
regex5 = r"(?i)debited \D*(?:Rs\.|INR)?\s*(\d+(?:\.\d+)?)"

# pattern for ambiguous sms
pattern_w = r"(?i).*(received|request|requested).*(received|request|requested)"
pattern_w1 = r"(?i).*(debited|debit)"

format = "%Y-%m-%d"  # used for extraction human-readable date from json date format

with open('data.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)
    s_time1 = re.sub("\D", '', "/Date(" + str(data[0]["date"]) + ")/")
    date_min1 = datetime.fromtimestamp(float(s_time1) / 1000).strftime('%Y-%m-%d')
    date_min = datetime.strptime(date_min1, format)
    date_max = date_min
    for x in range(len(data)):
        data[x]["body"] = data[x]["body"].replace(",", "")  # removing comma to read the amount in full form
        s_time1 = re.sub("\D", '', "/Date(" + str(data[x]["date"]) + ")/")
        d_time1 = datetime.fromtimestamp(float(s_time1) / 1000).strftime('%Y-%m-%d')
        d_time = datetime.strptime(d_time1, format)

        # calculation the range of dataset
        if date_min > d_time: date_min = d_time
        if date_max < d_time: date_max = d_time

    duration = (date_max - date_min).days

    print("we have sms data of total", (date_max - date_min).days, "that is from", date_min, "to", date_max)
    count_overdue = count_emi = 0
    sum = 0
    acc_bal_amt = acc_count = 0
    sum_debit_30 = sum_debit_60 = sum_debit_90 = sum_debit = 0
    count_debit_30 = count_debit_60 = count_debit_90 = count_debit = 0
    sum_credit_30 = sum_credit_60 = sum_credit_90 = sum_credit = 0
    count_credit_30 = count_credit_60 = count_credit_90 = count_credit = 0
    count_bounce_30 = count_bounce_60 = count_bounce_90 = count_bounce = 0
    count_decline_30 = count_decline_60 = count_decline_90 = count_decline = 0
    acc_bal_max_30 = acc_bal_max_60 = acc_bal_max_90 = acc_bal_max = 0
    acc_bal_min_30 = acc_bal_min_60 = acc_bal_min_90 = acc_bal_min = 0
    cnt_legal_90 = cnt_legal_60 = cnt_legal_30 = cnt_legal = 0
    cnt_neft_rtgs_imps_tran = cnt_neft_rtgs_imps_tran_30 = cnt_neft_rtgs_imps_tran_60 = cnt_neft_rtgs_imps_tran_90 = 0
    cnt_below_mab_penalty_occurances = cnt_below_mab_penalty_occurances_90 = cnt_below_mab_penalty_occurances_60 = cnt_below_mab_penalty_occurances_30 = 0
    sum_card_30 = sum_card_60 = sum_card_90 = sum_card = 0
    count_card_30 = count_card_60 = count_card_90 = count_card = 0
    sum_atm_30 = sum_atm_60 = sum_atm_90 = sum_atm = 0
    count_atm_30 = count_atm_60 = count_atm_90 = count_atm = 0
    str_temp = []
    date_sms = []
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
        val = 0  # pointer to decide later if sms if of financial type or promotional type

        s_time1 = re.sub("\D", '', "/Date(" + str(data[x]["date"]) + ")/")
        d1 = datetime.fromtimestamp(float(s_time1) / 1000).strftime('%Y-%m-%d')
        d = datetime.strptime(d1, format)
        decline_bit = 0
        msg = data[x]["body"]  # msg variable stores the body of the sms

        # check if msg contains the word EMI.
        if re.search(r".*EMI.*", msg, re.IGNORECASE):

            # check if it is a reminder message
            if re.search(r"\b(?:pending|overdue|due|earliest|clear|presented)\b", msg, re.IGNORECASE):
                count_overdue += 1
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
                count_emi += 1
                match1 = re.search(regex4, msg, re.IGNORECASE)
                match2 = re.search(regex5, msg, re.IGNORECASE)

                if match1:
                    match = match1
                elif match2:
                    match = match2
                if match1 or match2:
                    str_temp.append(msg)
                    val = 1
                    amountdebited.append(float(match.group(1)))
                    amountcredited.append(None)
                    amount.append(None)
                    category.append("EMI")
        elif re.match(pattern_w, msg):
            pass
        elif re.match(r'.*(legal notice)', msg, re.IGNORECASE):
            cnt_legal += 1

            # counting number of legal notices in different duration slabs
            if (date_max - d).days <= 30:
                cnt_legal_30 += 1
            if (date_max - d).days <= 60:
                cnt_legal_60 += 1
            if (date_max - d).days <= 90:
                cnt_legal_90 += 1

        # finding occurrences of declined payments
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
            count_decline += 1  # lifetime decline
            if (date_max - d).days <= 30:
                count_decline_30 += 1
            if (date_max - d).days <= 60:
                count_decline_60 += 1
            if (date_max - d).days <= 90:
                count_decline_90 += 1

        # finding the credit sms
        elif re.match(regex1, msg):
            match = re.match(regex1, msg)
            sum += float(match.group(2))
            amountcredited.append(float(match.group(2)))
            category.append("credit")
            amountdebited.append(None)
            str_temp.append(msg)
            amount.append(None)
            sum_credit += float(match.group(2))  # lifetime credit
            count_credit += 1

            # calculating sum of amt credited and number of credit transactions in different duration slabs
            if (date_max - d).days <= 30:
                sum_credit_30 += float(match.group(2))
                count_credit_30 += 1
            if (date_max - d).days <= 60:
                sum_credit_60 += float(match.group(2))
                count_credit_60 += 1
            if (date_max - d).days <= 90:
                sum_credit_90 += float(match.group(2))
                count_credit_90 += 1
            val = 1
        elif re.match(regex2, msg):
            match = re.match(regex2, msg)
            sum += float(match.group(2))
            amountcredited.append(float(match.group(2)))
            category.append("credit")
            amountdebited.append(None)
            str_temp.append(msg)
            amount.append(None)
            sum_credit += float(match.group(2))  # lifetime credit
            count_credit += 1

            # calculating sum of amt credited and number of credit transactions in different duration slabs
            if (date_max - d).days <= 30:
                sum_credit_30 += float(match.group(2))
                count_credit_30 += 1
            if (date_max - d).days <= 60:
                sum_credit_60 += float(match.group(2))
                count_credit_60 += 1
            if (date_max - d).days <= 90:
                sum_credit_90 += float(match.group(2))
                count_credit_90 += 1
            val = 1

        # special case of credit messages are dealt here where those sms aren't categorized which are actually debit sms
        # but provide information of account getting credited
        elif re.match(regex3, msg) and (not re.match(pattern_w1, msg)):
            match = re.match(regex3, msg)
            sum += float(match.group(2))
            amountcredited.append(float(match.group(2)))
            category.append("credit")
            amountdebited.append(None)
            str_temp.append(msg)
            amount.append(None)
            sum_credit += float(match.group(2))  # lifetime credit
            count_credit += 1

            # calculating sum of amt credited and number of credit transactions in different duration slabs
            if (date_max - d).days <= 30:
                sum_credit_30 += float(match.group(2))
                count_credit_30 += 1
            if (date_max - d).days <= 60:
                sum_credit_60 += float(match.group(2))
                count_credit_60 += 1
            if (date_max - d).days <= 90:
                sum_credit_90 += float(match.group(2))
                count_credit_90 += 1
            val = 1

        # categorizing bounce transactions
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
            count_bounce += 1  # lifetime bounce
            if (date_max - d).days <= 30:
                count_bounce_30 += 1
            if (date_max - d).days <= 60:
                count_bounce_60 += 1
            if (date_max - d).days <= 90:
                count_bounce_90 += 1

        # finding debit messages and amount debited
        elif re.search(regex4, msg):
            val = 1
            match = re.search(regex4, msg, re.IGNORECASE)
            amountdebited.append(float(match.group(1)))
            sum_debit += float(match.group(1))  # lifetime debit
            count_debit += 1

            # calculating sum of amt debited and number of debit transactions in different duration slabs
            if (date_max - d).days <= 30:
                sum_debit_30 += float(match.group(1))
                count_debit_30 += 1
            if (date_max - d).days <= 60:
                sum_debit_60 += float(match.group(1))
                count_debit_60 += 1
            if (date_max - d).days <= 90:
                sum_debit_90 += float(match.group(1))
                count_debit_90 += 1
            amountcredited.append(None)
            str_temp.append(msg)
            amount.append(None)
            category.append("debit")

        elif re.search(regex5, msg):
            match = re.search(regex5, msg, re.IGNORECASE)
            val = 1
            amountdebited.append(float(match.group(1)))
            sum_debit += float(match.group(1))  # lifetime debit
            count_debit += 1

            # calculating sum of amt debited and number of debit transactions in different duration slabs
            if (date_max - d).days <= 30:
                sum_debit_30 += float(match.group(1))
                count_debit_30 += 1
            if (date_max - d).days <= 60:
                sum_debit_60 += float(match.group(1))
                count_debit_60 += 1
            if (date_max - d).days <= 90:
                sum_debit_90 += float(match.group(1))
                count_debit_90 += 1
            amountcredited.append(None)
            str_temp.append(msg)
            amount.append(None)
            category.append("debit")

        if val == 1:
            # regex to find account numbers
            pattern = r"(?i)(A/c no.|a/c no.|ac no.|AC no.|Ac no.)\D*(\d+(?:\.\d+)?).*"
            pattern1 = r"(?i)(A/c |a/c |ac |AC |Ac |account XXXXXXXX|Account XXXXXXXX|account ending with)\D*(\d+(" \
                       r"?:\.\d+)?).*"
            pattern2 = r"(?i)(ef | Ref | Reference |txn |Txn )\D*(\d+(?:\.\d+)?).*"

            # regex to find transaction ids/reference numbers
            pattern3 = r"Ref\.No:(\d+)"  # to match the Ref No
            pattern4 = r"IMPS/P2A/(\d+)/(\d+)(?:/remar)?"  # to match the IMPS/P2A value
            pattern5 = r"NEFT.*?(\d+)"  # to extarct NEFT
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
            match6 = re.search(pattern5, msg, re.IGNORECASE)
            match7 = re.search(pattern6, msg, re.IGNORECASE)
            match8 = re.search(pattern7, msg, re.IGNORECASE)
            match9 = re.search(pattern8, msg, re.IGNORECASE)
            match10 = re.search(pattern9, msg, re.IGNORECASE)
            match11 = re.search(pattern10, msg, re.IGNORECASE)
            if decline_bit == 0:  # pointer to see if the sms is of type payment declined
                reason.append(None)

            date_sms.append(d)  # appending date for each sms to show in output Excel file

            # finding account number if present in the sms
            if match1:
                account_no.append(int(match1.group(2)[-4:]))
            elif match2:
                account_no.append(int(match2.group(2)[-4:]))
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
                transaction_id.append(match6.group(1))
            elif match7:
                transaction_id.append(match7.group(1))
            elif match8:
                transaction_id.append(match8.group(1))
            else:
                transaction_id.append(None)

            match1 = re.search(r'\b(balance|bal|bal ).*(Rs.|INR |Rs. |INR)(\d+)', msg)
            match2 = re.search(r'\b(balance|bal|bal ).*(Rs. -|INR -)(\d+)', msg)

            # finding account balance from sms
            if match1:
                acc_bal.append(float(match1.group(3)))
                acc_bal_amt += float(match1.group(3))
                acc_count += 1

                # comparing account balances to find the maximum and minimum values in different duration slabs
                if float(match1.group(3)) > acc_bal_max:
                    acc_bal_max = float(match1.group(3))
                elif float(match1.group(3)) < acc_bal_min:
                    acc_bal_min = float(match1.group(3))
                if (date_max - d).days <= 30:
                    if float(match1.group(3)) > acc_bal_max_30:
                        acc_bal_max_30 = float(match1.group(3))
                    elif float(match1.group(3)) < acc_bal_min_30:
                        acc_bal_min_30 = float(match1.group(3))
                if (date_max - d).days <= 60:
                    if float(match1.group(3)) > acc_bal_max_60:
                        acc_bal_max_60 = float(match1.group(3))
                    elif float(match1.group(3)) < acc_bal_min_60:
                        acc_bal_min_60 = float(match1.group(3))
                if (date_max - d).days <= 90:
                    if float(match1.group(3)) > acc_bal_max_90:
                        acc_bal_max_90 = float(match1.group(3))
                    elif float(match1.group(3)) < acc_bal_min_90:
                        acc_bal_min_90 = float(match1.group(3))

            elif match2:
                acc_bal.append(int(match2.group(3)) * (-1))
                acc_bal_amt += int(match2.group(3)) * (-1)
                acc_count += 1

                # comparing account balances to find the minimum value in different duration slabs
                if int(match2.group(3)) * (-1) < acc_bal_min:
                    acc_bal_min = int(match2.group(3)) * (-1)
                if (date_max - d).days <= 30 and int(match2.group(3)) * (-1) < acc_bal_min_30:
                    acc_bal_min_30 = int(match2.group(3)) * (-1)
                if (date_max - d).days <= 60 and int(match2.group(3)) * (-1) < acc_bal_min_60:
                    acc_bal_min_60 = int(match2.group(3)) * (-1)
                if (date_max - d).days <= 90 and int(match2.group(3)) * (-1) < acc_bal_min_90:
                    acc_bal_min_90 = int(match2.group(3)) * (-1)
            else:
                acc_bal.append(None)

            # counting the neft,imps and rtgs transactions according to date slabs
            if match5 or match6:
                cnt_neft_rtgs_imps_tran += 1
                if (date_max - d).days <= 30: cnt_neft_rtgs_imps_tran_30 += 1
                if (date_max - d).days <= 60: cnt_neft_rtgs_imps_tran_60 += 1
                if (date_max - d).days <= 90: cnt_neft_rtgs_imps_tran_90 += 1

            if match9:
                amount_card = float(match9.group(1).replace(',', ''))
                count_card += 1
                sum_card += amount_card
                if (date_max - d).days <= 30:
                    count_card_30 += 1
                    sum_card_30 += amount_card
                if (date_max - d).days <= 60:
                    count_card_60 += 1
                    sum_card_60 += amount_card
                if (date_max - d).days <= 90:
                    count_card_90 += 1
                    sum_card_90 += amount_card
            # finding atm transactions sum and count in different time slabs
            elif match10 or match11:
                if match10:
                    match = match10
                else:
                    match = match11
                amount_atm = float(match.group(1).replace(',', ''))
                count_atm += 1
                sum_atm += amount_atm
                if (date_max - d).days <= 30:
                    count_atm_30 += 1
                    sum_atm_30 += amount_atm
                if (date_max - d).days <= 60:
                    count_atm_60 += 1
                    sum_atm_60 += amount_atm
                if (date_max - d).days <= 90:
                    count_atm_90 += 1
                    sum_atm_90 += amount_atm

        if bool(re.search(r'\b(mab)\b', msg, re.IGNORECASE)):  # finding mab occurrences in different duration slabs
            cnt_below_mab_penalty_occurances += 1
            if (date_max - d).days <= 30: cnt_below_mab_penalty_occurances_30 += 1
            if (date_max - d).days <= 60: cnt_below_mab_penalty_occurances_60 += 1
            if (date_max - d).days <= 90: cnt_below_mab_penalty_occurances_90 += 1

    avg_acc_bal = int(acc_bal_amt / acc_count)  # avg account balance
    # Create a new DataFrame with messages and amounts debited
    new_df = pd.DataFrame({'Message': str_temp, 'Amount Debited': amountdebited, 'Amount Credited': amountcredited,
                           'Account Number': account_no, 'Transaction ID': transaction_id, "Amount": amount,
                           "Category": category, "reason": reason, "Account Balance": acc_bal, "Date": date_sms})

    # Save the new DataFrame to a new Excel file
    new_df.to_excel('messages_with_amountsV2.xlsx', index=False)

    # computing parameters for debit transactions
    cnt_avg_daily_debit_trans = count_debit / duration
    cnt_avg_daily_debit_trans_90 = count_debit_90 / 90
    cnt_avg_daily_debit_trans_60 = count_debit_60 / 60
    cnt_avg_daily_debit_trans_30 = count_debit_30 / 30
    ratio_cnt_avg_daily_debit_trans_30_to_90 = cnt_avg_daily_debit_trans_30 / cnt_avg_daily_debit_trans_90
    ratio_cnt_avg_daily_debit_trans_30_to_60 = cnt_avg_daily_debit_trans_30 / cnt_avg_daily_debit_trans_60
    amt_avg_daily_debit_trans = int(sum_debit / duration)
    amt_avg_daily_debit_trans_90 = int(sum_debit_90 / 90)
    amt_avg_daily_debit_trans_60 = int(sum_debit_60 / 60)
    amt_avg_daily_debit_trans_30 = int(sum_debit_30 / 30)
    ratio_amt_avg_daily_debit_trans_30_to_90 = amt_avg_daily_debit_trans_30 / amt_avg_daily_debit_trans_90
    ratio_amt_avg_daily_debit_trans_30_to_60 = amt_avg_daily_debit_trans_30 / amt_avg_daily_debit_trans_60
    amt_avg_debit_per_trans = sum_debit / count_debit
    amt_avg_debit_per_trans_90 = sum_debit_90 / count_debit_90
    amt_avg_debit_per_trans_60 = sum_debit_60 / count_debit_60
    amt_avg_debit_per_trans_30 = sum_debit_30 / count_debit_30
    ratio_amt_avg_debit_per_trans_30_to_90 = amt_avg_debit_per_trans_30 / amt_avg_daily_debit_trans_90
    ratio_amt_avg_debit_per_trans_30_to_60 = amt_avg_debit_per_trans_30 / amt_avg_daily_debit_trans_60

    print("Count of avg daily debit transactions", cnt_avg_daily_debit_trans)
    print("Count of avg daily debit transactions for last 90 days is", cnt_avg_daily_debit_trans_90)
    print("amount of average debit transaction is", amt_avg_debit_per_trans)
    print("ratio of average amount debited daily within last 30 days to last 90 days is ",
          ratio_amt_avg_daily_debit_trans_30_to_90)
    print("ratio of average amount debited daily per transaction within last 30 days to last 90 days is ",
          ratio_amt_avg_debit_per_trans_30_to_90)

    # computing parameters for credit transactions
    cnt_avg_daily_credit_trans = count_credit / duration
    cnt_avg_daily_credit_trans_90 = count_credit_90 / 90
    cnt_avg_daily_credit_trans_60 = count_credit_60 / 60
    cnt_avg_daily_credit_trans_30 = count_credit_30 / 30
    ratio_cnt_avg_daily_credit_trans_30_to_90 = cnt_avg_daily_credit_trans_30 / cnt_avg_daily_credit_trans_90
    ratio_cnt_avg_daily_credit_trans_30_to_60 = cnt_avg_daily_credit_trans_30 / cnt_avg_daily_credit_trans_60
    amt_avg_daily_credit_trans = int(sum_credit / duration)
    amt_avg_daily_credit_trans_90 = int(sum_credit_90 / 90)
    amt_avg_daily_credit_trans_60 = int(sum_credit_60 / 60)
    amt_avg_daily_credit_trans_30 = int(sum_credit_30 / 30)
    ratio_amt_avg_daily_credit_trans_30_to_90 = amt_avg_daily_credit_trans_30 / amt_avg_daily_credit_trans_90
    ratio_amt_avg_daily_credit_trans_30_to_60 = amt_avg_daily_credit_trans_30 / amt_avg_daily_credit_trans_60
    amt_avg_credit_per_trans = sum_credit / count_credit
    amt_avg_credit_per_trans_90 = sum_credit_90 / count_credit_90
    amt_avg_credit_per_trans_60 = sum_credit_60 / count_credit_60
    amt_avg_credit_per_trans_30 = sum_credit_30 / count_credit_30
    ratio_amt_avg_credit_per_trans_30_to_90 = amt_avg_credit_per_trans_30 / amt_avg_daily_credit_trans_90
    ratio_amt_avg_credit_per_trans_30_to_60 = amt_avg_credit_per_trans_30 / amt_avg_daily_credit_trans_60

    ratio_total_debit_to_credit_amount = sum_debit / sum_credit
    ratio_total_debit_to_credit_amount_90 = sum_debit_90 / sum_credit_90
    ratio_total_debit_to_credit_amount_60 = sum_debit_60 / sum_credit_60
    ratio_total_debit_to_credit_amount_30 = sum_debit_30 / sum_credit_30

    print("similarly we can find the same parameters for credit transactions:")
    print(cnt_avg_daily_credit_trans)
    print(cnt_avg_daily_credit_trans_90)
    print(amt_avg_credit_per_trans)
    print(ratio_cnt_avg_daily_credit_trans_30_to_90)
    print(ratio_amt_avg_credit_per_trans_30_to_90)
    print("customer has had total", cnt_below_mab_penalty_occurances, "below mab occurences")
    print("total number of neft/imps/rtgs payments have been", cnt_neft_rtgs_imps_tran)
    print("customer has average account balance", avg_acc_bal)
    print("number of payments declined have been", count_decline)

    # plotting graphs
    categories = ['legal notices', 'below mab occurrences', 'debited successfully', 'declined payments', 'bounced '
                                                                                                         'transactions']
    values = [cnt_legal, cnt_below_mab_penalty_occurances, count_debit, count_decline, count_bounce]
    fig = plt.figure(figsize=(12, 7))
    plt.pie(values, labels=categories)

    # show plot
    plt.show()

    barWidth = 0.25
    fig = plt.subplots(figsize=(12, 8))

    # set height of bar
    IT = [sum_debit_30, sum_debit_60, sum_debit_90, sum_debit]
    ECE = [sum_credit_30, sum_credit_60, sum_credit_90, sum_credit]
    IT1 = [amt_avg_daily_debit_trans_30, amt_avg_daily_debit_trans_60, amt_avg_daily_debit_trans_90,
           amt_avg_daily_debit_trans]
    ECE1 = [amt_avg_daily_credit_trans_30, amt_avg_daily_credit_trans_60, amt_avg_daily_credit_trans_90,
            amt_avg_daily_credit_trans]
    # Set position of bar on X axis
    br1 = np.arange(len(IT))
    br2 = [x + barWidth for x in br1]

    # Make the plot
    plt.bar(br1, IT, color='r', width=barWidth,
            edgecolor='grey', label='debit')
    plt.bar(br2, ECE, color='g', width=barWidth,
            edgecolor='grey', label='credit')

    # Adding Xticks
    plt.xlabel('Duration slabs', fontweight='bold', fontsize=15)
    plt.ylabel('Amount', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(IT))],
               ['Last 30 days', 'Last 60 days', 'Last 90 days', 'Total'])

    plt.title("Total amount credited and debited according to duration slabs")
    plt.legend()
    plt.show()

    plt.bar(br1, IT1, color='r', width=barWidth,
            edgecolor='grey', label='debit')
    plt.bar(br2, ECE1, color='g', width=barWidth,
            edgecolor='grey', label='credit')

    # Adding Xticks
    plt.xlabel('Duration slabs', fontweight='bold', fontsize=15)
    plt.ylabel('Amount', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(IT))],
               ['Last 30 days', 'Last 60 days', 'Last 90 days', 'Total'])

    plt.title("Total amount credited and debited on average on daily basis according to duration slabs")
    plt.legend()
    plt.show()

json_file.close()
workbook.save('complete_data.xlsx')

parser.plot()
