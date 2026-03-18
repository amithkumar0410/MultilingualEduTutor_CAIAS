
from flask import Flask, request, redirect, session, render_template
from pymongo import MongoClient

import random
import smtplib
from email.mime.text import MIMEText

=======
from flask import Flask, request, jsonify, render_template

from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from deep_translator import GoogleTranslator
from google import genai
import os
<<<<<<< HEAD


YOUR_KEY = os.getenv("GEMINI_API_KEY")
client2 = genai.Client(api_key=YOUR_KEY)
=======
YOUR_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=YOUR_KEY)

def getanswer(text):
    data=f"""
        Explain: {text}

            Rules:
            - Maximum 5 lines
            - Each line short (under 12 words)
            - No extra text
            - No long paragraphs

            Format:
            1.
            2.
            3.
            4.
            5.
            """
    try:
        # 3. Test a simple call
<<<<<<< HEAD
        response = client2.models.generate_content(
=======
        response = client.models.generate_content(
>>>>>>> 29d90277d7b071a4472dc1b120af73ec2b5afc00
            model="models/gemini-2.5-flash",
            
            contents=data
        )
        return response.text
    except Exception as e:

        return f"Error: {str(e)}"
=======
        return e


def translate(text,l="en"):
    try:
        translated = GoogleTranslator(source="auto", target=l).translate(text)
        return translated
    except Exception as e:
        return f"Error: here {l} {e}"






app = Flask(__name__)
app.secret_key = "secret123"

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "auth_db"

SENDER = "thinkersinfinty@gmail.com"
PASSWORD = "wruq fttg khtk pocr"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db["users"]
users.create_index("email", unique=True)
chati=client["chati"]
def generate_otp():
    return str(random.randint(100000, 999999))

def send_email(to_email, otp):
    msg = MIMEText(f"Your OTP is {otp}")
    msg['Subject'] = "OTP Verification"
    msg['From'] = SENDER
    msg['To'] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email error:", e)
        return False

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if users.find_one({"email": email}):
            return "Email already exists"

        otp = generate_otp()

        session["temp_user"] = {
            "email": email,
            "password": password,
            "otp": otp
        }

        if not send_email(email, otp):
            return "Failed to send email"

        return redirect("/verify")

    return render_template("register.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        user_otp = request.form["otp"]
        temp_user = session.get("temp_user")

        if not temp_user:
            return "Session expired"

        if user_otp == temp_user["otp"]:
            users.insert_one({
                "email": temp_user["email"],
                "password": temp_user["password"]
            })
            session.pop("temp_user", None)
            return redirect("/login")
        else:
            return "Invalid OTP"

    return render_template("verify.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users.find_one({"email": email,"password":password})

        if user:
            return render_template("chat.html")
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route('/send', methods=['POST'])
def send_message():
    try:
        user_text = request.json.get('text')
        lang = request.json.get("lan", "en")

        if not user_text:
            return jsonify({"error": "No text provided"}), 400

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trans = translate(user_text)
        ans = getanswer(trans)
        fresult = translate(ans, l=lang)
        
        # Save both parts to MongoDB to restore them later
        user_doc = {"text": user_text, "sender": "user", "timestamp": datetime.now(), "date_str": ""}
        sys_doc = {"text": fresult, "sender": "system", "timestamp": datetime.now(), "date_str": current_date}
        
        chati.insert_many([user_doc, sys_doc])
        
        return jsonify({"reply": fresult, "date": current_date})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Error: {str(e)}", "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
=======
        
app = Flask(__name__)
CORS(app)

client2 = MongoClient("mongodb://localhost:27017/")
db = client2.chat_database
messages_col = db.messages

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/send', methods=['POST'])
def send_message():
    user_text = request.json.get('text')
    lang = request.json.get("lan")

  
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trans= translate(user_text)
    ans=getanswer(trans)
    fresult= translate(ans,l=lang)
    
    # Save both parts to MongoDB to restore them later
    user_doc = {"text": user_text, "sender": "user", "timestamp": datetime.now(), "date_str": ""}
    sys_doc = {"text": fresult, "sender": "system", "timestamp": datetime.now(), "date_str": current_date}
    
    messages_col.insert_many([user_doc, sys_doc])
    
    return jsonify({"reply": fresult, "date": current_date})
>>>>>>> 29d90277d7b071a4472dc1b120af73ec2b5afc00
    
   
@app.route('/history', methods=['GET'])
def get_history():

    try:
        history = list(chati.find({}, {"_id": 0}).sort("timestamp", 1))
        return jsonify(history)
    except Exception as e:
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True,port=8080)
=======
    history = list(messages_col.find({}, {"_id": 0}).sort("timestamp", 1))
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True,port=8080)

