from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
from groq import Groq
import torch
import re
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
app.debug = True
app.secret_key = os.getenv("APP_SECRET_KEY")
app.logger.setLevel(logging.INFO)

# Dynamic model path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "Model")

# Function to load model and tokenizer
def load_model_and_tokenizer():
    """
    Load model and tokenizer from local directory or download from HuggingFace.
    Supports dynamic model paths for deployment.
    """
    try:
        # Try loading from local Model directory first
        if os.path.exists(MODEL_DIR):
            print(f"📦 Loading model from {MODEL_DIR}")
            tokenizer = DistilBertTokenizer.from_pretrained(MODEL_DIR)
            model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
        else:
            # Fallback to pretrained model from HuggingFace
            print("📥 Downloading model from HuggingFace...")
            model_name = "distilbert-base-uncased"
            tokenizer = DistilBertTokenizer.from_pretrained(model_name)
            model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=2)
            
            # Save for future use
            os.makedirs(MODEL_DIR, exist_ok=True)
            model.save_pretrained(MODEL_DIR)
            tokenizer.save_pretrained(MODEL_DIR)
            print(f"✅ Model saved to {MODEL_DIR}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("⚠️ Using base DistilBERT model")
        tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
        model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
    
    model.eval()
    return model, tokenizer

# Load model and tokenizer
model, tokenizer = load_model_and_tokenizer()

# ------------------ GROQ CLIENT ------------------ #
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ------------------ UNREADABLE TEXT CHECK ------------------ #
def is_unreadable(text):
    text = text.strip()

    # Rule 1: Very short text
    if len(text) < 4:
        return True

    # Rule 2: Contains no meaningful words (all single-type characters)
    if re.fullmatch(r"[A-Za-z]{4,}", text) and len(set(text)) <= 3:
        return True

    # Rule 3: Mostly repeated characters
    if len(set(text)) <= 2 and len(text) > 5:
        return True

    # Rule 4: Contains almost no vowels → likely gibberish
    vowels = sum(c.lower() in "aeiou" for c in text)
    if vowels == 0:
        return True

    # Rule 5: Contains mostly non-alphabet symbols
    alpha = sum(c.isalpha() for c in text)
    ratio = alpha / len(text)
    if ratio < 0.3:
        return True

    # Rule 6: No spaces + too long + no dictionary structure
    if (" " not in text) and len(text) > 8 and vowels <= 1:
        return True

    return False


# ------------------ BERT PREDICTION ------------------ #
def predict_intent(text):

    if is_unreadable(text):
        return "Not Interested / Will Not Buy", "red"

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()

    label_map = {
        0: ("Not Interested / Will Not Buy", "red"),
        1: ("Interested / Will Buy", "green")
    }

    return label_map.get(predicted_class, ("Unknown", "black"))


# ------------------ GROQ GENERATIVE AI SUMMARY ------------------ #
def generate_intent_analysis(text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert in analyzing customer purchase intent. Answer in 2–3 lines."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content


# ------------------ ROUTES ------------------ #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        app.logger.info(f"Login attempt: username={username!r} password={'***' if password else None}")
        
        # Hardcoded credentials
        if username == "joel" and password == "joel@123":
            session["user"] = username
            app.logger.info(f"Login success: setting session user={username}")
            return redirect(url_for("home"))
        else:
            app.logger.info("Login failed: invalid credentials")
            return render_template("login.html", error="Invalid username or password")
    
    # Check if already logged in
    if "user" in session:
        return redirect(url_for("home"))
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/")
def home():
    # Check if user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    # Check if user is logged in
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_text = request.form.get("user_input")

    # 1. DistilBERT prediction
    prediction_text, prediction_color = predict_intent(user_text)

    # 2. Groq Llama3 generative explanation
    gen_ai_output = generate_intent_analysis(user_text)

    return jsonify({
        "prediction_text": prediction_text,
        "prediction_color": prediction_color,
        "gen_ai_output": gen_ai_output
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
