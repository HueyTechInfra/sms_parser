import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# from main import sum_debit_30, sum_credit_60, sum_debit_60, cnt_legal, cnt_below_mab_penalty_occurances,
# count_decline, \ count_debit, count_bounce, amt_avg_daily_credit_trans_30, amt_avg_daily_credit_trans,
# amt_avg_daily_credit_trans_60, \ amt_avg_daily_credit_trans_90, amt_avg_daily_debit_trans_90,
# amt_avg_daily_debit_trans_60, \ amt_avg_daily_debit_trans_30, amt_avg_daily_debit_trans, sum_credit_30, sum_credit,
# sum_debit, sum_debit_90, \ sum_credit_90


def comp():
    file = 'messages_with_amountsV2.xlsx'

    newData = pd.read_excel(file)
    acc_no = []  # contains account number corresponding to every sms

    credit = []
    debit = []
    acc = []
    amt_cr = []
    amt_db = []
    for x in newData['Account Number']:
        if x > 0: acc_no.append(x)
    res = []
    [res.append(x) for x in acc_no if x not in res]  # res contains unique account numbers
    acc_no = []
    for x in newData['Account Number']: acc_no.append(x)
    for x in newData['Amount Credited']:
        amt_cr.append(x)
    for x in newData['Amount Debited']:
        amt_db.append(x)
    for acc in res:
        sum_cr = sum_db = 0
        for i in range(len(acc_no)):
            if acc_no[i] == acc:
                if amt_cr[i] > 0:
                    sum_cr += amt_cr[i]
                elif amt_db[i] > 0:
                    sum_db += amt_db[i]
        credit.append(sum_cr)
        debit.append(sum_db)

    # eliminating accounts having no credit/debit ie they belong to different category
    temp = []
    for i in range(len(credit)):
        if credit[i] == 0 and debit[i] == 0:
            temp.append(i)
    for i in range(len(temp)):
        del res[temp[i] - i]
        del credit[temp[i] - i]
        del debit[temp[i] - i]
    fig = plt.figure(figsize=(10, 5))
    for i in range(len(res)):
        res[i] = str(res[i])

    print(res)
    print(credit)
    print(debit)
    barWidth = 0.25
    fig = plt.subplots(figsize=(12, 8))
    br1 = np.arange(len(credit))
    br2 = [x + barWidth for x in br1]

    # Make the plot
    plt.bar(br1, credit, color='g', width=barWidth,
            edgecolor='grey', label='credit')
    plt.bar(br2, debit, color='r', width=barWidth,
            edgecolor='grey', label='debit')

    # Adding Xticks
    plt.xlabel('Account Numbers', fontweight='bold', fontsize=15)
    plt.ylabel('Amount', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(res))],
               res)
    plt.title("Amount credited and debited for each account of customer")
    plt.legend()
    plt.show()

    # plot to show distribution of all messages among different categories
    cat = []
    for x in newData['Category']:
        cat.append(x)
    res1 = []
    [res1.append(x) for x in cat if x not in res1]
    count = [0] * len(res1)
    for i in range(len(res1)):
        for j in range(len(cat)):
            if cat[j] == res1[i]: count[i] += 1

    fig = plt.figure(figsize=(12, 7))
    plt.pie(count, labels=res1)

    # show plot
    plt.show()



