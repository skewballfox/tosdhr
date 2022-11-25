from transformers import AutoTokenizer, AutoModelForPreTraining

tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")

model = AutoModelForPreTraining.from_pretrained("nlpaueb/legal-bert-base-uncased")

# TODO!!!!!!!!!!!
