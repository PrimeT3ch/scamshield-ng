"""Train a small TF-IDF + logistic regression scam classifier and report honest metrics."""
import pandas as pd, joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("data.csv")
model = make_pipeline(
    make_union(
        TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True),
    ),
    LogisticRegression(max_iter=2000, class_weight="balanced", C=10),
)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
pred = cross_val_predict(model, df.text, df.label, cv=cv)
print(classification_report(df.label, pred, target_names=["ok", "scam"]))
print(confusion_matrix(df.label, pred))
model.fit(df.text, df.label)
joblib.dump(model, "model.joblib")
print("saved model.joblib")
