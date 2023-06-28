# Importing the libraries needed
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch import cuda
import seaborn as sns
import transformers
import json
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaModel, RobertaTokenizer
import logging

logging.basicConfig(level=logging.ERROR)

device = 'cuda' if cuda.is_available() else 'cpu'

# Load the Excel file
df = pd.read_excel('messages_with_amountsV2.xlsx')
new_df = df[['Message', 'Category']]

# Get the columns for amount and date
amount_column = 'Message'
cat_column = 'Category'
msgs = []
category = []

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    # Get the amount and date from the respective columns
    amount = row[amount_column]
    cat = row[cat_column]
    msgs.append(amount)
    category.append(cat)

# Defining some key variables that will be used later on in the training
MAX_LEN = 256
TRAIN_BATCH_SIZE = 8
VALID_BATCH_SIZE = 4
# EPOCHS = 1
LEARNING_RATE = 1e-05
tokenizer = RobertaTokenizer.from_pretrained('roberta-base', truncation=True, do_lower_case=True)


class SentimentData(Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.text = dataframe.Phrase
        self.targets = self.data.Sentiment
        self.max_len = max_len

    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        text = str(self.text[index])
        text = " ".join(text.split())

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            pad_to_max_length=True,
            return_token_type_ids=True
        )
        ids = inputs['input_ids']
        mask = inputs['attention_mask']
        token_type_ids = inputs["token_type_ids"]

        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
            'targets': torch.tensor(self.targets[index], dtype=torch.float)
        }


train_size = 0.8
train_data = new_df.sample(frac=train_size, random_state=200)
test_data = new_df.drop(train_data.index).reset_index(drop=True)
train_data = train_data.reset_index(drop=True)

print("FULL Dataset: {}".format(new_df.shape))
print("TRAIN Dataset: {}".format(train_data.shape))
print("TEST Dataset: {}".format(test_data.shape))

training_set = SentimentData(train_data, tokenizer, MAX_LEN)
testing_set = SentimentData(test_data, tokenizer, MAX_LEN)

train_params = {'batch_size': TRAIN_BATCH_SIZE,
                'shuffle': True,
                'num_workers': 0
                }

test_params = {'batch_size': VALID_BATCH_SIZE,
               'shuffle': True,
               'num_workers': 0
               }

training_loader = DataLoader(training_set, **train_params)
testing_loader = DataLoader(testing_set, **test_params)


class RobertaClass(torch.nn.Module):
    def __init__(self):
        super(RobertaClass, self).__init__()
        self.l1 = RobertaModel.from_pretrained("roberta-base")
        self.pre_classifier = torch.nn.Linear(768, 768)
        self.dropout = torch.nn.Dropout(0.3)
        self.classifier = torch.nn.Linear(768, 5)

    def forward(self, input_ids, attention_mask, token_type_ids):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        hidden_state = output_1[0]
        pooler = hidden_state[:, 0]
        pooler = self.pre_classifier(pooler)
        pooler = torch.nn.ReLU()(pooler)
        pooler = self.dropout(pooler)
        output = self.classifier(pooler)
        return output


model = RobertaClass()
model.to(device)

# dataset = {'train': [], 'test': []}
# for x in range(0, 2000):
#     dataset["train"].append({'label': category[x], 'text': msgs[x]})
# for x in range(2000, len(dataset)):
#     dataset["test"].append({'label': category[x], 'text': msgs[x]})
# training_size = 500
# training_sentences = msgs[0:training_size]
# validation_sentences = msgs[training_size:]
# training_labels = category[0:training_size]
# validation_labels = category[training_size:]
# tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
#
# train_encodings = tokenizer(training_sentences,
#                             truncation=True,
#                             padding=True)
# val_encodings = tokenizer(validation_sentences,
#                           truncation=True,
#                           padding=True)
#
# train_dataset = tf.data.Dataset.from_tensor_slices((
#     dict(train_encodings),
#     training_labels
# ))
# val_dataset = tf.data.Dataset.from_tensor_slices((
#     dict(val_encodings),
#     validation_labels
# ))
#
#
# def tokenize(batch):
#     return tokenizer(batch["text"], padding=True, truncation=True)
#
#
# model_id = "cardiffnlp/twitter-roberta-base-sentiment"
# class_names = training_labels
# # Create an id2label mapping
# id2label = {i: label for i, label in enumerate(class_names)}
#
# # Update the model's configuration with the id label mapping
# config = AutoConfig.from_pretrained(model_id)
# config.update({"id2label": id2label})
# model = RobertaForSequenceClassification.from_pretrained(model_id, config=config)
# repository_id = "cardiffnlp/twitter-roberta-base-sentiment"
# training_args = TrainingArguments(
#     output_dir=repository_id,
#     num_train_epochs=5,
#     per_device_train_batch_size=8,
#     per_device_eval_batch_size=8,
#     evaluation_strategy="epoch",
#     logging_dir=f"{repository_id}/logs",
#     logging_strategy="steps",
#     logging_steps=10,
#     learning_rate=5e-5,
#     weight_decay=0.01,
#     warmup_steps=500,
#     save_strategy="epoch",
#     load_best_model_at_end=True,
#     save_total_limit=2,
#     report_to="tensorboard",
#     push_to_hub=True,
#     hub_strategy="every_save",
#     hub_model_id=repository_id,
#     hub_token=HfFolder.get_token(),
# )
#
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=val_dataset,
# )
#
# # Fine-tune the model
# trainer.train()
