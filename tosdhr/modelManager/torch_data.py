import torch
import numpy as np
from numpy.typing import NDArray
from transformers import AutoTokenizer

# from torch.utils.data import

# labels = {"business": 0, "entertainment": 1, "sport": 2, "tech": 3, "politics": 4}
tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")


class Dataset(torch.utils.data.Dataset):
    def __init__(self, raw_text: list[str], case_ids: list[int]):

        self.labels = [case_id for case_id in case_ids]
        self.texts = [
            tokenizer(
                text,
                padding="max_length",
                max_length=512,
                truncation=True,
                return_tensors="pt",
            )
            for text in raw_text
        ]
        print(self.texts)

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
