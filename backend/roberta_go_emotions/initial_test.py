from os import mkdir

from transformers import pipeline

classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

# load sentences from file 
with open("sentences.txt", "r", encoding="utf-8") as f:
    full_sentences = f.read().replace("\n", " ").strip()

sentences = [full_sentences]


model_outputs = classifier(sentences, truncation=True, max_length=512)


with open("initial_test_output.json", "w", encoding="utf-8") as f:
    import json
    json.dump(model_outputs, f, indent=4)