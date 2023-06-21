import json
import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

msgs = []

# code for guessing the salary_date and amount
format = "%Y-%m-%d"  # used for extraction human-readable date from json date format
with open('new-parser/newdata4.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)
    s_time1 = re.sub("\D", '', "/Date(" + str(data[0]["date"]) + ")/")
    date_min1 = datetime.fromtimestamp(float(s_time1) / 1000).strftime('%Y-%m-%d')
    date_min = datetime.strptime(date_min1, format)
    date_max = date_min
    for x in range(len(data)):
        msgs.append(data[x]["body"])
        data[x]["body"] = data[x]["body"].replace(",", "")  # removing comma to read the amount in full form
        s_time1 = re.sub("\D", '', "/Date(" + str(data[x]["date"]) + ")/")
        d_time1 = datetime.fromtimestamp(float(s_time1) / 1000).strftime('%Y-%m-%d')
        d_time = datetime.strptime(d_time1, format)

        # calculation the range of dataset
        if date_min > d_time:
            date_min = d_time
        if date_max < d_time:
            date_max = d_time

    duration = (date_max - date_min).days
json_file.close()

duration = int(duration / 30)
file = 'messages_with_amountsV2.xlsx'
d = pd.read_excel(file)
salary = []
date = []
month = []
year = []
for i in range(len(d['Amount Credited'])):
    x = d['Amount Credited'][i]
    if x > 0:
        salary.append(x)
        date.append(d['Date'][i])
        month.append(d['Date'][i])
        year.append(d['Date'][i])
for i in range(len(date)):
    t = date[i]
    t.to_pydatetime()
    date[i] = t.day
    month[i] = t.month
    year[i] = t.year
min_month = month[-1]
min_year = year[-1]
max_month = month[0]
max_year = year[0]
lst = []
for k in range(32):
    temp = []
    for i in range(len(date)):
        if date[i] == k:
            temp.append(salary[i])
    lst.append(temp)
lst_old = lst.copy()
count = 0
for i in range(len(lst)):
    if len(lst[i - count]) < 0.7 * duration:
        del [lst[i - count]]
        count += 1
date_sal = []
for i in range(len(lst)):
    mx_amt = 0
    for k in range(len(lst[i])):
        count = 0
        amt = lst[i][k]
        for t in range(len(lst[i])):
            if amt + 5000 >= lst[i][t] >= amt - 5000:
                count += 1
        if count >= (0.7 * duration) + 1 and amt > mx_amt:
            mx_amt = amt
            if i not in date_sal:
                date_sal.append(i)
final_date = []
salary_date = -1
for x in range(len(lst_old)):
    for i in date_sal:
        if lst_old[x] == lst[i]:
            final_date = lst_old[x]
            salary_date = x
mx = 1
amt = 0  # the variable storing the salary guessed by the script
for k in final_date:
    count = 0
    for t in final_date:
        if k + 5000 >= t >= k - 5000:
            count += 1

    if count >= (0.7 * duration) + 1 and amt < k:
        amt = k

# plotting code according to salary_date and salary_amount which is guessed by the script

salary_date = 30
amt = 15000
final_temp = [[]] * 5
# storing amounts credited on dates 2 before and 2 after the mentioned date and amount if found in buffer range of
# 5000, only then mentioned
for x in range(-2, 3):
    temp_year = min_year
    temp_month = min_month
    temp_lst = []
    temp = [None] * 12
    for i in range(-1, -len(date), -1):
        if year[i] > temp_year:
            temp_lst.append(temp)
            temp = [None] * 12
            temp_month = 1
            temp_year += 1
        elif date[i] == salary_date + x and amt + 5000 >= salary[i] >= amt - 5000:
            if temp[month[i] - 1] is None:
                temp[month[i] - 1] = salary[i]
            else:
                temp[month[i] - 1] = max(temp[month[i] - 1], salary[i])
    temp_lst.append(temp)
    final_temp[x + 2] = temp_lst
for i in range(-2, 3):
    for x in range(len(final_temp[0])):
        for y in range(0, 12):
            if final_temp[i + 2][x][y] is None:
                final_temp[i + 2][x][y] = 0

temp_lst = final_temp[0]
temp_lst1 = final_temp[1]
temp_lst2 = final_temp[2]
temp_lst3 = final_temp[3]
temp_lst4 = final_temp[4]

# making sum_plot array from the arrays generated earlier to use it for plotting
# this array will contain the average sum for every 10 months

temp_month = min_month
temp_year = 0
sum_plot = []
duration = int(duration / 10)
for i in range(duration):
    sum = 0
    for j in range(10):
        if temp_month < 12:
            if temp_lst2[temp_year][temp_month - 1] != 0:
                sum += temp_lst2[temp_year][temp_month - 1]
            else:
                sum += max(max(temp_lst[temp_year][temp_month - 1], temp_lst1[temp_year][temp_month - 1]),
                           max(temp_lst3[temp_year][temp_month - 1], temp_lst4[temp_year][temp_month - 1]))

        else:
            temp_month = (temp_month % 12) + 1
            temp_year += 1
            j -= 1
        temp_month += 1
    sum_plot.append(sum)

for i in range(len(sum_plot)):
    sum_plot[i] = sum_plot[i] / 10
category = []
for i in range(len(sum_plot)):
    temp = "Last" + str((i + 1) * 10) + "months"
    category.append(temp)
# creating the bar plot
fig = plt.figure(figsize=(10, 5))
plt.bar(category, sum_plot, color='blue', width=0.4)

plt.xlabel("duration slabs")
plt.ylabel("avg salary credited")
plt.title("average salary for every 10 months")
plt.show()
