# -*- coding: utf-8 -*-
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import random

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def compute_age(data):
    d, m, y = data.get("dob_day"), data.get("dob_month"), data.get("dob_year")
    try:
        if d and m and y:
            month = int(m) if m.isdigit() else datetime.strptime(m, "%B").month
            bd = datetime(int(y), month, int(d))
            today = datetime.today()
            return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except:
        return None

def generate_child_summary(name, gender, age, country, visual, auditory, kinesthetic, daily_review, self_motivated, group_learning, math, reading, focus):
    return f"""在{country}，许多年约{age}岁的{'男孩' if gender == 'Male' else '女孩'}正处于探索学习风格的关键阶段。数据显示，视觉学习偏好占比达 {visual}%，远高于听觉（{auditory}%）与动觉（{kinesthetic}%）学习方式。这反映出，图像、颜色和故事性内容更容易激发这个年龄段孩子的学习兴趣。父母若能多使用图像化教材和互动式演示，孩子的专注力和理解力将显著提升。

进一步分析学习习惯，约有 {daily_review}% 的孩子已养成每日复习的习惯，显示出早期的自律倾向。而 {self_motivated}% 展现出独立学习的能力，是培养终身学习者的基础。相比之下，仅有 {group_learning}% 喜欢小组互动，或许说明孩子更偏好在安静或熟悉的环境中学习。家长可尝试以温和引导方式，鼓励轻松的小组分享，逐步提升孩子的协作能力。

在核心学科方面，数学表现领先（{math}%），阅读能力次之（{reading}%），而专注力则处于相对较低的水平（{focus}%）。这组数据提示我们，虽然学术基础稳固，但注意力的培养仍是关键。建议结合音乐引导、定时学习法与适度休息，帮助孩子找到最适合自己的学习节奏，减少分心情况。

整体来看，这份报告不仅是一组数字，更是孩子成长的缩影。每一个比例背后都是一个努力的身影。父母和教育者可借助这些洞察，调整教学策略，平衡学术发展与情绪支持。在新加坡、马来西亚和台湾，越来越多家庭正以个性化方式支持孩子迈向全面成长的旅程。"""

@app.route("/analyze_name_zh", methods=["POST"])
def analyze_name():
    data = request.json
    name = data.get("name")
    gender = data.get("gender")
    country = data.get("country")
    age = compute_age(data)

    # Random chart values
    visual = random.randint(40, 85)
    auditory = random.randint(20, 50)
    kinesthetic = random.randint(10, 30)
    daily_review = random.randint(30, 60)
    self_motivated = random.randint(25, 60)
    group_learning = random.randint(15, 45)
    math = random.randint(60, 90)
    reading = random.randint(50, 75)
    focus = random.randint(30, 60)

    summary = generate_child_summary(name, gender, age, country, visual, auditory, kinesthetic, daily_review, self_motivated, group_learning, math, reading, focus)

    # Fix f-string issue by pre-processing summary
    summary_html = summary.replace('\n', '<br><br>')

    # Compose email body
    email_html = f"""
    <html><body style='font-family:sans-serif;color:#333'>
    <h2>🎯 新提交记录：</h2>
    <p>👤 <strong>姓名：</strong>{name}<br>
    🌏 <strong>国家：</strong>{country}<br>
    🧒 <strong>性别：</strong>{gender}<br>
    🎂 <strong>年龄：</strong>{age}</p>
    <hr>
    <h3>📊 学习分析图表</h3>
    <ul>
      <li>视觉学习：{visual}%</li>
      <li>听觉学习：{auditory}%</li>
      <li>动觉学习：{kinesthetic}%</li>
      <li>每日复习：{daily_review}%</li>
      <li>独立学习：{self_motivated}%</li>
      <li>小组互动：{group_learning}%</li>
      <li>数学表现：{math}%</li>
      <li>阅读表现：{reading}%</li>
      <li>专注能力：{focus}%</li>
    </ul>
    <hr>
    <h3>🧠 报告概览</h3>
    <p>{summary_html}</p>
    </body></html>
    """

    # Email sending
    try:
        msg = MIMEText(email_html, 'html', 'utf-8')
        msg['Subject'] = "全球 AI 学习洞察"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "summary": summary,
        "chart_data": {
            "visual": visual,
            "auditory": auditory,
            "kinesthetic": kinesthetic,
            "daily_review": daily_review,
            "self_motivated": self_motivated,
            "group_learning": group_learning,
            "math": math,
            "reading": reading,
            "focus": focus
        }
    })

if __name__ == "__main__":
    app.run(debug=True)
