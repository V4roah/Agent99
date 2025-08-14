from typing import Iterable
from dataclasses import dataclass
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import csv, os

MODEL_PATH = "models/clf.joblib"

@dataclass
class TrainItem:
    text: str
    label: str

def load_seed_csv(path: str) -> list[TrainItem]:
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            out.append(TrainItem(text=row["text"], label=row["label"]))
    return out

def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1,2), max_features=30000)),
        ("clf", LinearSVC())
    ])

def train_and_save(data: Iterable[TrainItem]) -> str:
    X = [d.text for d in data]
    y = [d.label for d in data]
    pipe = build_pipeline()
    pipe.fit(X, y)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    dump(pipe, MODEL_PATH)
    return MODEL_PATH

def predict(texts: list[str]) -> list[str]:
    pipe: Pipeline = load(MODEL_PATH)
    return pipe.predict(texts).tolist()
