from torch import nn

import torch
from torch.optim import Adam
from torch import cuda, device as torch_device, squeeze
from tqdm import tqdm
from torch.utils.data import Dataset as torchDataset, DataLoader as torchDataLoader
from transformers import AutoTokenizer, AutoModelForPreTraining


class Annotator(nn.Module):
    def __init__(self, dropout=0.05):
        super(Annotator, self).__init__()
        self.bert = AutoModelForPreTraining.from_pretrained(
            "nlpaueb/legal-bert-base-uncased"
        )
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, 5)
        self.relu = nn.ReLU()

    def forward(self, input_ids, attention_mask):
        # _, pooled_output = self.bert(
        #     input_ids=input_ids, attention_mask=attention_mask, return_dict=False
        # )
        bert_output, _ = self.bert(
            input_ids=input_ids, attention_mask=attention_mask, return_dict=False
        )
        dropout_output = self.dropout(pooled_output)
        linear_output = self.linear(dropout_output)
        final_layer = self.relu(linear_output)

        return linear_output  # Return the output of the linear layer


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
        print("about to call model")


class BertForPreTraining(BertPreTrainedModel):
    ...
    def forward(...):
        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
        )

        sequence_output, pooled_output = outputs[:2]
        sequence_output, output_lm_labels = gather_indexes_auto(sequence_output, masked_lm_labels)

        prediction_scores, seq_relationship_score = self.cls(sequence_output, pooled_output)

        outputs = (prediction_scores, seq_relationship_score,) + outputs[
            2:
        ]  # add hidden states and attention if they are here

        if masked_lm_labels is not None and next_sentence_label is not None:
            loss_fct = CrossEntropyLoss()
            masked_lm_loss = loss_fct(prediction_scores.view(-1, self.config.vocab_size), output_lm_labels.view(-1))
            next_sentence_loss = loss_fct(seq_relationship_score.view(-1, 2), next_sentence_label.view(-1))
            total_loss = masked_lm_loss + next_sentence_loss
            outputs = (total_loss,) 

        return outputsgi