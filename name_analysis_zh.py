# -*- coding: utf-8 -*-
import os, smtplib, logging, random, unicodedata
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

CHINESE_MONTHS = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4,
    '五月': 5, '六月': 6, '七月': 7, '八月': 8,
    '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}

def normalize_month(s):
    if s is None:
        return ''
    s = s.strip()
    s = unicodedata.normalize('NFKC', s)
    return s

def send_email(html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "New KataChatBot Submission"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info("✅ Email sent successfully")
    except Exception as e:
        logging.error("❌ Email failed to send: %s", str(e))

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    data = request.get_json()
    name = data.get("full_name", "").strip()
    dob_day = int(data.get("dob_day", 1))
    dob_month_raw = data.get("dob_month")
    dob_month = normalize_month(dob_month_raw)
    dob_year = int(data.get("dob_year", 2000))

    if dob_month in CHINESE_MONTHS:
        month = CHINESE_MONTHS[dob_month]
    elif dob_month.isdigit():
        month = int(dob_month)
    else:
        try:
            month = datetime.strptime(dob_month, "%B").month
        except Exception as e:
            return jsonify({"error": f"Invalid month: {dob_month}"}), 400

    try:
        birthdate = datetime(dob_year, month, dob_day)
    except Exception as e:
        return jsonify({"error": "Invalid date."}), 400

    # Placeholder response for success
    summary = f"<p>Full Name: {name}</p><p>Birthdate: {birthdate.strftime('%Y-%m-%d')}</p>"
    send_email(summary)
    return jsonify({"message": "Month parsed and email sent successfully.", "birthdate": birthdate.strftime("%Y-%m-%d")})

if __name__ == "__main__":
    app.run(debug=True)
