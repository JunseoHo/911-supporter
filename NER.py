from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

model_name = "dslim/bert-base-NER"
cut_off = 0.9

model = AutoModelForTokenClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

while True:
    example = input("Text: ")
    ner_results = nlp(example)
    print(ner_results)
