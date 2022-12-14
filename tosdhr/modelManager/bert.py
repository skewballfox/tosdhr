from torch import nn

import torch
from torch.optim import Adam
from torch import cuda, device as torch_device, squeeze
from tqdm import tqdm
from torch.utils.data import Dataset as torchDataset, DataLoader as torchDataLoader
from transformers import AutoTokenizer, AutoModelForPreTraining


# train(model, df_train, df_val)


class Annotator(nn.Module):
    def __init__(self, dropout=0.05):
        super(Annotator, self).__init__()
        self.bert = AutoModelForPreTraining.from_pretrained(
            "nlpaueb/legal-bert-base-cased"
        )
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, 5)
        self.relu = nn.ReLU()

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(
            input_ids=input_ids, attention_mask=attention_mask, return_dict=False
        )

        # Convert bert_output to Tensor
        dropout_output = self.dropout(pooled_output)
        linear_output = self.linear(dropout_output)
        final_layer = self.relu(linear_output)
        return final_layer


def train(
    model: Annotator,
    train_data: torchDataset,
    validation_data: torchDataset,
    learning_rate=1e-6,
    epochs=5,
    use_cpu=False,
):
    print("starting train")
    train_dataloader = torchDataLoader(train_data, batch_size=2, shuffle=True)
    validation_dataloader = torchDataLoader(validation_data, batch_size=2)
    use_cuda: bool = cuda.is_available() if not use_cpu else False
    device: torch_device = torch_device("cuda" if use_cuda else "cpu")
    criterion: nn.CrossEntropyLoss = nn.CrossEntropyLoss()
    optimizer: Adam = Adam(model.parameters(), lr=learning_rate)
    print("past optimizer")
    if use_cuda:
        model: Annotator = model.cuda()
        criterion = criterion.cuda()
    print("starting epochs")
    for epoch_num in range(epochs):
        print(epoch_num)
        total_acc_train = 0
        total_loss_train = 0
        print("about to call model train")
        model.train()
        print("called model train")
        for train_input, train_label in tqdm(train_dataloader):
            # print(train_input)
            # print(train_label)
            train_label = train_label.to(device)
            mask = train_input["attention_mask"].to(device)
            print("Made it past mask")
            input_id = train_input["input_ids"].to(device)
            print("Made it past input_id")
            # input_ids, which should be (batch_size, seq_length)
            # Make input_id = input_id first and last index
            input_id = input_id[:, 0, :]
            print(input_id)
            print("")
            print(mask)
            output = model.forward(input_id, mask)  # PROBLEM HERE
            print("Made it past output")
            print(output)
            # THIS IS FOR TESTING
            ######################################################################

            ######################################################################
            batch_loss = criterion(output, train_label.long())
            total_loss_train += batch_loss.item()
            acc = (output.argmax(dim=1) == train_label).sum().item()
            total_acc_train += acc
            model.zero_grad()
            batch_loss.backward()
            optimizer.step()
        total_acc_val = 0
        total_loss_val = 0
        print("past for loop")
        with torch.no_grad():
            for val_input, val_label in validation_dataloader:
                val_label = val_label.to(device)
                mask = val_input["attention_mask"].to(device)
                input_id = squeeze(val_input["input_ids"].to(device), 1)
                output = model(input_id, mask)
                batch_loss = criterion(output, val_label.long())
                total_loss_val += batch_loss.item()
                acc = (output.argmax(dim=1) == val_label).sum().item()
                total_acc_val += acc
        print(
            f"Epochs: {epoch_num + 1} | Train Loss: {total_loss_train / len(train_data): .3f} \
                | Train Accuracy: {total_acc_train / len(train_data): .3f} \
                | Val Loss: {total_loss_val / len(validation_data): .3f} \
                | Val Accuracy: {total_acc_val / len(validation_data): .3f}"
        )


def evaluate(model: Annotator, test_data: torchDataset, use_cpu=False):
    test_dataloader = torch.utils.data.DataLoader(test_data, batch_size=2)
    use_cuda = torch.cuda.is_available() if not use_cpu else False
    device = torch.device("cuda" if use_cuda else "cpu")

    if use_cuda:
        model = model.cuda()

    total_acc_test = 0
    with torch.no_grad():
        for test_input, test_label in test_dataloader:
            test_label = test_label.to(device)
            mask = test_input["attention_mask"].to(device)
            input_id = test_input["input_ids"].squeeze(1).to(device)
            output = model(input_id, mask)
            acc = (output.argmax(dim=1) == test_label).sum().item()
            total_acc_test += acc

    print(f"Test Accuracy: {total_acc_test / len(test_data): .3f}")


# What do you need me to work on?
# should we use the discord or the session chat?
