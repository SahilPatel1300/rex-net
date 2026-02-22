import os
from pathlib import Path

# set project root 
project_root = Path(__file__).resolve().parent.parent
# make imgs dir if it doesn't exist
os.makedirs("imgs", exist_ok=True)

list_of_emotions = ["admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism", "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"]
# make sub folders for each emotion
for emotion in list_of_emotions:
    os.makedirs(project_root / "imgs" / emotion, exist_ok=True)

print("imgs dir created")

# make a .gitignore file in the imgs dir
with open(project_root / "imgs" / ".gitignore", "w") as f:
    f.write("*")
    