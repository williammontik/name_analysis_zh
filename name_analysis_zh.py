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

# Chinese month mapping
CHINESE_MONTHS = {
    "一月": 1, "二月": 2, "三月": 3, "四月": 4,
    "五月": 5, "六月": 6, "七月": 7, "八月": 8,
    "九月": 9, "十月": 10, "十一月": 11, "十二月": 12
}

def send_email(html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "New Child Learning Submission"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USERNAME, SMTP_PASSWORD)
            s.send_message(msg)
        logging.info("✅ Email sent successfully")
    except Exception:
        logging.exception("❌ Email sending failed")

def generate_child_metrics():
    return [
        {"title": "学习偏好", "labels": ["视觉型", "听觉型", "动手实践型"],
         "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]},
        {"title": "学习投入", "labels": ["每日复习", "小组学习", "自主学习"],
         "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]},
        {"title": "学业信心", "labels": ["数学", "阅读", "专注力"],
         "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]}
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"In {country}, many children around age {age} are showing unique learning patterns. Visual: {metrics[0]['values'][0]}%, Auditory: {metrics[0]['values'][1]}%, Kinesthetic: {metrics[0]['values'][2]}%.",
        f"Study involvement — Daily review: {metrics[1]['values'][0]}%, Group study: {metrics[1]['values'][1]}%, Independent: {metrics[1]['values'][2]}%.",
        f"Academic confidence — Math: {metrics[2]['values'][0]}%, Reading: {metrics[2]['values'][1]}%, Focus: {metrics[2]['values'][2]}%.",
        "These trends show how children in the region are developing. With care and guidance, they can reach their full potential with the right support at home and school."
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 Summary:</div><br>" + \
        "".join(f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>{p}</p>" for p in paragraphs)

@app.route('/analyze_name', methods=['POST'])
def analyze_name():
    try:
        data = request.get_json(force=True)
        app.logger.info("📥 Incoming data: %s", data)

        name = data.get('name', '').strip()
        chinese_name = data.get('chinese_name', '').strip()
        gender = data.get('gender', '').strip()
        country = data.get('country', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        referrer = data.get('referrer', '').strip()
        dob_day = str(data.get("dob_day")).strip()
        dob_month = str(data.get("dob_month")).strip()
        dob_year = str(data.get("dob_year")).strip()

        if not (dob_day and dob_month and dob_year):
            return jsonify({'error': 'Missing birthdate fields.'}), 400

        try:
            if dob_month in CHINESE_MONTHS:
                month = CHINESE_MONTHS[dob_month]
            elif dob_month.isdigit():
                month = int(dob_month)
            else:
                month = datetime.strptime(dob_month, "%B").month
        except Exception as e:
            logging.exception("❌ Month parsing failed")
            return jsonify({'error': f'Month parsing error: {dob_month}'}), 400

        try:
            birthdate = datetime(int(dob_year), month, int(dob_day))
        except Exception as e:
            logging.exception("❌ Birthdate construction failed")
            return jsonify({'error': 'Invalid birthdate values'}), 400

        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        if age < 2 or age > 21:
            return jsonify({'error': f'Age {age} is outside expected range.'}), 400

        metrics = generate_child_metrics()
        summary = generate_child_summary(age, gender, country, metrics)
        html_result = generate_summary_html(summary)

        email_html = f"""
        <html><body style='font-family:sans-serif; color:#333'>
        <h2>🎯 New Submission:</h2>
        <p>
        👤 Name: {name}<br>
        🈶 Chinese Name: {chinese_name}<br>
        ⚧️ Gender: {gender}<br>
        🎂 DOB: {birthdate.date()}<br>
        🕑 Age: {age}<br>
        🌍 Country: {country}<br>
        📞 Phone: {phone}<br>
        📧 Email: {email}<br>
        💬 Referrer: {referrer}
        </p>
        <hr><h2>📊 AI Summary</h2>
        {html_result}
        </body></html>
        """

        send_email(email_html)

        return jsonify({
            "metrics": metrics,
            "analysis": html_result
        })
    except Exception:
        logging.exception("❌ Fatal error in /analyze_name")
        return jsonify({'error': 'Server crashed while processing'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
