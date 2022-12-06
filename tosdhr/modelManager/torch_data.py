import torch
import numpy as np
from numpy.typing import NDArray
from transformers import AutoTokenizer
from pandas import DataFrame

# from torch.utils.data import

# labels = {"business": 0, "entertainment": 1, "sport": 2, "tech": 3, "politics": 4}
tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")


def train_val_test_split(df: DataFrame):
    np.random.seed(112)

    df_train, df_val, df_test = np.split(
        df.sample(frac=1, random_state=42), [int(0.8 * len(df)), int(0.9 * len(df))]
    )
    return Dataset(df_train), Dataset(df_val), Dataset(df_test)


class Dataset(torch.utils.data.Dataset):
    def __init__(self, df: DataFrame):
        print(df["case"])
        self.labels = [case_id for case_id in set(df["case"])]

        self.texts = [
            tokenizer(
                text,
                padding="max_length",
                max_length=512,
                truncation=True,
                return_tensors="pt",
            )
            for text in df["text"]
        ]

    def classes(self):
        return self.labels

    def __len__(self) -> int:
        return len(self.labels)

    def get_batch_labels(self, idx) -> NDArray:
        # Fetch a batch of labels
        return np.array(self.labels[idx])

    def get_batch_texts(self, idx):
        # Fetch a batch of inputs
        return self.texts[idx]

    def __getitem__(self, idx):

        batch_texts = self.get_batch_texts(idx)
        batch_y = self.get_batch_labels(idx)

        return batch_texts, batch_y
