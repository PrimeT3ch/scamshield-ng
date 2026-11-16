import os, re, json, joblib, requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
model = joblib.load("model.joblib")

# Simple rule-based red flags, shown even when no LLM key is set.
FLAGS = [
    (r"\botp\b|\bpin\b|\bpassword\b|\btoken\b|\bbvn\b|\bnin\b|\bcode\b|verification code", "Mentions a secret (OTP, PIN, password, BVN, NIN or code). Real banks never ask you to send these."),
    (r"https?://|bit\.ly|\.xyz|\.top|click", "Pushes you to click a link. Open your bank app yourself instead."),
    (r"urgent|immediately|now now|within \\d+ hours|blocked|suspended|restricted|deactivat|expire", "Creates panic and urgency so you act without thinking."),
    (r"won|congratulations|free|grant|palliative|prince|guaranteed|double", "Promises money or prizes you did not ask for."),
    (r"fee|pay \d|send \d|registration", "Asks you to pay first before you receive anything."),
]

SAFE_WARNING = re.compile(r"never share|do not share|don't share|will never ask", re.I)

def red_flags(text):
    flags = []
    for pat, msg in FLAGS:
        if re.search(pat, text, re.I):
            # A message that WARNS you not to share a secret is not asking for it.
            if msg.startswith("Mentions a secret") and SAFE_WARNING.search(text):
                continue
            flags.append(msg)
    return flags or ["No common scam red flags found by the rules. Still check with your bank if unsure."]

def llm_explain(text, score, flags, lang):
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return "AI explanation is off: OPENROUTER_API_KEY is not set."
    style = "Pidgin English" if lang == "pidgin" else "simple English"
    prompt = (f"A classifier gave this message a scam risk of {score:.0%}. Message: \"\"\"{text}\"\"\"\n"
              f"Detected flags: {flags}\nIn 3 short sentences of {style}, explain why it is or isn't "
              "suspicious and what the person should do. Do not invent facts about the sender.")
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": os.getenv("OPENROUTER_MODEL", "openrouter/free"),
                  "messages": [{"role": "user", "content": prompt}]}, timeout=30)
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "AI explanation unavailable right now (the model did not respond). The score and red flags above still apply."

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/check")
def check():
    d = request.get_json(force=True)
    text = (d.get("text") or "").strip()[:1000]
    if not text:
        return jsonify(error="Paste a message first"), 400
    score = float(model.predict_proba([text])[0][1])
    flags = red_flags(text)
    level = "HIGH" if score >= 0.7 else "MEDIUM" if score >= 0.4 else "LOW"
    explanation = llm_explain(text, score, flags, d.get("lang", "english"))
    return jsonify(score=score, level=level, flags=flags,
                   explanation=explanation)

if __name__ == "__main__":
    app.run(debug=True)
