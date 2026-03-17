from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from deep_translator import GoogleTranslator
from google import genai
import os
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
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            
            contents=data
        )
        return response.text
    except Exception as e:
        return e

def translate(text,l="en"):
    try:
        translated = GoogleTranslator(source="auto", target=l).translate(text)
        return translated
    except Exception as e:
        return f"Error: here {l} {e}"
        
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
    
   
@app.route('/history', methods=['GET'])
def get_history():
    history = list(messages_col.find({}, {"_id": 0}).sort("timestamp", 1))
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True,port=8080)