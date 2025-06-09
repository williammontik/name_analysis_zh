# -*- coding: utf-8 -*-
import os, smtplib, logging, random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "新儿童学习表单提交"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USERNAME, SMTP_PASSWORD)
            s.send_message(msg)
        logging.info("✅ 邮件发送成功")
    except Exception:
        logging.exception("❌ 邮件发送失败")

def generate_child_metrics():
    return [
        {"title":"学习偏好","labels":["视觉","听觉","动手"],"values":[random.randint(50,70),random.randint(25,40),random.randint(10,30)]},
        {"title":"学习参与","labels":["每日复习","小组学习","自主学习"],"values":[random.randint(40,60),random.randint(20,40),random.randint(30,50)]},
        {"title":"学业信心","labels":["数学","阅读","专注力"],"values":[random.randint(50,85),random.randint(40,70),random.randint(30,65)]}
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在{country}，大约{age}岁的{gender}孩子正以独特方式踏入学习阶段。视觉学习占比 {metrics[0]['values'][0]}%，听觉 {metrics[0]['values'][1]}%，动手 {metrics[0]['values'][2]}%。",
        f"学习参与方面：每日复习 {metrics[1]['values'][0]}%，小组学习 {metrics[1]['values'][1]}%，自主学习 {metrics[1]['values'][2]}%。",
        f"学业信心方面：数学 {metrics[2]['values'][0]}%，阅读 {metrics[2]['values'][1]}%，专注 {metrics[2]['values'][2]}%。",
    ]

@app.route('/analyze_name', methods=['POST'])
def analyze_name():
    try:
        data = request.get_json(force=True)
        name = data.get('name','').strip()
        if not name:
            return jsonify({'error':'请输入孩子姓名。'}),400
        chinese_name = data.get('chinese_name','').strip()
        gender = data.get('gender','')
        country = data.get('country','')
        dob = f"{data.get('dob_year')}-{data.get('dob_month')}-{data.get('dob_day')}"
        year, month, day = int(data.get('dob_year')), int(data.get('dob_month')), int(data.get('dob_day'))
        birth = datetime(year, month, day)
        today = datetime.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        metrics = generate_child_metrics()
        paragraphs = generate_child_summary(age, gender, country, metrics)
        analysis = "<br>".join(paragraphs)
        html_email = f"<h2>新儿童数据：</h2><p>姓名：{name}<br>中文名：{chinese_name}<br>性别：{gender}<br>年龄：{age}<br>国家：{country}</p><hr><h3>分析结果：</h3><p>{analysis}</p>"
        send_email(html_email)
        return jsonify({'metrics':metrics,'analysis':analysis})
    except Exception:
        logging.exception("处理 analyze_name 时发生错误")
        return jsonify({'error':'服务器内部错误。'}),500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
