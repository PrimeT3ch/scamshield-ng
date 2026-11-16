"""Score held-out REAL messages (never used for training). Threshold 0.4 = MEDIUM or higher."""
import pandas as pd, joblib
model = joblib.load("model.joblib")
df = pd.concat([pd.read_csv("real_test.csv"), pd.read_csv("real_normal_test.csv")], ignore_index=True)
df["score"] = model.predict_proba(df.text)[:, 1]
df["flagged"] = (df.score >= 0.4).astype(int)
for _, r in df.iterrows():
    print(f"{r.score:.0%}  label={'scam' if r.label else 'normal'}  flagged={bool(r.flagged)}  {r.type}")
s, n = df[df.label == 1], df[df.label == 0]
print(f"\nScams caught: {int(s.flagged.sum())}/{len(s)}")
print(f"Normal messages wrongly flagged: {int(n.flagged.sum())}/{len(n)}")
