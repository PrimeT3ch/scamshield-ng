# ScamShield NG

A scam message checker for Nigeria. Paste a suspicious SMS or WhatsApp message and get a risk score, the red flags found, and a plain-language explanation in English or Pidgin.

Built for the AI OpenBuild hackathon on Devpost.

**Demo video:** https://youtu.be/kr6a39iE26o

## Who it is for
People who receive messages like fake bank alerts, "send me the code" requests, fake jobs and fake investments, and have no quick way to check them before acting. Global Anti-Scam Alliance, *State of Scams in Nigeria 2026*, reports that 84% of Nigerian adults encountered a scam in the past year and 22% lost money.

## How it works
1. **Classifier:** a TF-IDF (word and character n-grams) + logistic regression model, trained with scikit-learn, gives a scam risk score.
2. **Red-flag rules:** simple patterns spot PIN/OTP/BVN requests, links, urgency and upfront fees. A message that *warns* you not to share a code is not flagged for it.
3. **AI explanation:** a language model (via OpenRouter, free `openrouter/free` router) explains the result in English or Pidgin.

Example input and output:

    Input:  Your Kuda account is restricted. Click kuda-verify.top and enter your PIN to restore access today
    Output: HIGH risk (93%)
            - Mentions a secret (OTP, PIN, password, BVN, NIN or code)
            - Pushes you to click a link
            - Creates panic and urgency
            + AI explanation in English or Pidgin

## Run it
    pip install -r requirements.txt
    python train.py
    set OPENROUTER_API_KEY=your_key      (Windows; use export on Mac/Linux)
    python app.py

Open http://127.0.0.1:5000. Without a key the app still shows the score and red flags. Never commit an API key.

## Testing and honest results
- **Cross-validation on my own training data (96 messages): about 94% accuracy.** Do not trust this number. The messages were short and written by me with AI help, so it is optimistic.
- **Held-out real messages (`real_test.csv`, `real_normal_test.csv`, 10 messages never used for training):** caught **5 of 5** real scams but wrongly flagged **3 of 5** normal messages. A first version (words only) flagged all 10, so switching to word plus character features helped, but the model is still not reliable.
- Run `python evaluate.py` to reproduce the held-out test.

## Limitations
- The training set is tiny, so scores are not well calibrated. Long, varied real messages (bank safety emails, service notices) are often wrongly flagged.
- Red-flag rules are keyword-based and miss scams that avoid those words (for example a fake "I sent money by mistake" transfer request).
- The AI explanation can repeat a wrong assumption, and the free model changes between requests, so wording varies.
- Pidgin support covers the AI explanation and a few training examples only.
- It is a prototype and is not a substitute for calling your bank on the number printed on your card.

## Data, credits and AI assistance
- `data.csv`: 96 labelled messages written for this project with AI assistance, modelled on common scam patterns. No personal data.
- `real_test.csv`, `real_normal_test.csv`: 10 real messages received by the author, with names, numbers and links removed.
- Built during the hackathon: everything in this repository. Pre-existing components: open-source libraries only (Flask, scikit-learn, pandas, joblib, requests).
- AI assistance: the code, dataset, explainer video and narration were built with help from Claude (Anthropic). Narration uses the open-source Kokoro text-to-speech model.
- Statistics: Global Anti-Scam Alliance, State of Scams in Nigeria 2026.

## Team
Prince Iliya (solo): idea, testing, real-message collection, and project direction.
