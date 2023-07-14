# sms_parser
sms parser using python and concept of regex to categorize various types of financial messages and fetch various useful features from the sms provided in the dataset

main.py contains the script that is run on data.json reading the body of each text sms and date of sms received. The script creates an excel file for the output.

Using the various scripts of different banks according to the user sms dataset we are trying to categorize each sms into different main categories such as transactions, one time passwords, promotional messages or information messages and rest is others. Further according to the sender of the sms we categorize the sms into bank,wallet,upi,fastag,etc. Lastly, we categorize the sms into credit,debit,emi,otp,standing instructions, salary or any other reason of payment getting failed like insufficient balances or credit card limit being exceeded. 

We try to fetch different parameters like amount, account number, transaction id from the sms by parsing it through our regular expressions. Most of the regular expressions are general but some have been tweaked according to bank specific to improve accuracy and enable the parser to categorize some unique categories. 

The flow of the script is to try to parse the sms body into different possibilities of categories of sms. First it checks if it is a sms of loan disbursal or information regarding loan being processed. Then it check emi debit,promotional msgs, transactions of various kinds, respectively. 

If the sms does not fall into any of the above category then it gets checked for e-commerce related msgs or any defaulter sort of sms. 

At last it tries to fetch account balance if present, account number if present or transaction id if present in the sms. 
Any bank specific tweaks that are made in the reex are mentioned in form of comments along the regex. All the regex are mentioned at top of the script except the regex being used to fetch account number, account balance and transaction id which are present at the bottom. All the loops are labeled using comments in order to justify their purpose.
