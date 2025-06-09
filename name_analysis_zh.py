# -*- coding: utf-8 -*-
import os, smtplib, logging, random
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

CHINESE_GENDER = {
    '男': 'male',
    '女': 'female'
}

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
        logging.error("❌ Email sending failed", exc_info=True)

def generate_child_metrics():
    return [
        {
            "title": "Learning Preferences",
            "labels": ["Visual", "Auditory", "Kinesthetic"],
            "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]
        },
        {
            "title": "Study Engagement",
            "labels": ["Daily Review", "Group Study", "Independent Effort"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "Academic Confidence",
            "labels": ["Math", "Reading", "Focus & Attention"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def translate_month(month_str):
    if month_str in CHINESE_MONTHS:
        return CHINESE_MONTHS[month_str]
    try:
        return int(month_str) if month_str.isdigit() else datetime.strptime(month_str.capitalize(), "%B").month
    except:
        raise ValueError(f"Invalid month format: {month_str}")

def translate_gender(gender):
    return CHINESE_GENDER.get(gender, gender)

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        logging.info("[analyze_name] Payload received")

        name = data.get("name", "").strip()
        chinese_name = data.get("chinese_name", "").strip()
        gender = translate_gender(data.get("gender", "").strip())
        country = data.get("country", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        referrer = data.get("referrer", "").strip()

        month = translate_month(data.get("dob_month", "").strip())
        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_paragraphs = generate_child_summary(age, gender, country, metrics)
        summary_only_html = generate_summary_html(summary_paragraphs)
        charts_html = generate_email_charts(metrics)
        email_html_result = build_email_report(summary_only_html, charts_html)

        email_html = f"""<html><body style='font-family:sans-serif;color:#333'>
        <h2>🎯 New User Submission:</h2>
        <p>
        👤 <strong>Full Name:</strong> {name}<br>
        🈶 <strong>Chinese Name:</strong> {chinese_name}<br>
        ⚧️ <strong>Gender:</strong> {gender}<br>
        🎂 <strong>DOB:</strong> {birthdate.date()}<br>
        🕑 <strong>Age:</strong> {age}<br>
        🌍 <strong>Country:</strong> {country}<br>
        📞 <strong>Phone:</strong> {phone}<br>
        📧 <strong>Email:</strong> {email}<br>
        💬 <strong>Referrer:</strong> {referrer}
        </p>
        <hr><h2>📊 AI-Generated Report</h2>
        {email_html_result}
        </body></html>"""

        send_email(email_html)
        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ Error in /analyze_name")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
