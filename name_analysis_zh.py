# -*- coding: utf-8 -*-
import os
import smtplib
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        pass
    return None


def generate_child_summary(age, gender, country, visual, auditory, kinesthetic, daily_review, self_motivated, group_learning, math, reading, focus):
    para1 = f"在{country}，许多年龄在{age}岁左右的{'男孩' if gender == 'male' else '女孩'}，正安静地踏上学习旅程。数据显示，{visual}% 的孩子偏好视觉学习，如图像与色彩，{auditory}% 倾向听觉学习，{kinesthetic}% 偏好动手实践。视觉化内容如故事书、图表或影像，有助激发他们的理解与兴趣，是启发他们想象力的重要桥梁。"

    para2 = f"从学习习惯来看，{daily_review}% 的孩子已经养成每天复习的好习惯，这显示了他们具备基本的自律能力。同时，有 {self_motivated}% 的孩子在没有他人引导的情况下也能保持专注，展现了独立学习的潜力。相比之下，仅有 {group_learning}% 经常参与小组互动，这或许说明他们在社交性学习上还需要更多鼓励，家长可以透过亲子共读、小型学习圈等方式温柔引导。"

    para3 = f"在关键学科表现方面，{math}% 的孩子展现出对数学的理解力，{reading}% 在阅读方面表现良好，而专注力指数为 {focus}% 则反映了他们在面对干扰时的应对能力。建议采用规律作息、分段学习、轻音乐辅助等策略，以帮助他们提升专注水平。"

    para4 = f"整体而言，这些数据不仅是冰冷的数字，更勾勒出孩子内在成长的轮廓。他们正在努力理解这个世界，而来自家长与教育者的理解与支持，将是他们前行的温暖力量。在新加坡、马来西亚与台湾地区，越来越多家庭也开始探索如何平衡学术与情绪教育，让孩子在获得知识的同时，也感受到被看见、被肯定的力量。"

    return "\n\n".join([para1, para2, para3, para4])


@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.json
        name = data.get("full_name")
        gender = data.get("gender")
        country = data.get("country")
        age = compute_age(data)

        # Randomized chart data
        visual = random.randint(50, 80)
        auditory = random.randint(20, 50)
        kinesthetic = random.randint(10, 30)
        daily_review = random.randint(30, 60)
        self_motivated = random.randint(30, 60)
        group_learning = random.randint(20, 40)
        math = random.randint(60, 85)
        reading = random.randint(50, 75)
        focus = random.randint(30, 60)

        summary = generate_child_summary(age, gender, country, visual, auditory, kinesthetic, daily_review, self_motivated, group_learning, math, reading, focus)

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
        <p>{summary.replace('\n', '<br><br>')}</p>
        </body></html>
        """

        send_email(email_html)

        return jsonify({
            "summary": summary,
            "chart": {
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def send_email(html_body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "新儿童学习分析报告"
    msg['From'] = SMTP_USERNAME
    msg['To'] = SMTP_USERNAME
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, SMTP_USERNAME, msg.as_string())


if __name__ == "__main__":
    app.run(debug=True)
