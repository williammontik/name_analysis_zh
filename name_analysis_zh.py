# -*- coding: utf-8 -*-
import os
import smtplib
from datetime import datetime
from dateutil import parser
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from openai import OpenAI
import base64
import matplotlib.pyplot as plt
import io
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
    return "未知"

def generate_child_summary(data):
    age = data.get("age", "未知")
    gender = data.get("gender", "")
    country = data.get("country", "本地")
    gender_label = "男孩" if gender == "Male" else "女孩"

    visual_pct = data.get("visual_learning", 0)
    audio_pct = data.get("auditory_learning", 0)
    action_pct = data.get("kinesthetic_learning", 0)

    review_pct = data.get("daily_review", 0)
    solo_pct = data.get("independent_learning", 0)
    group_pct = data.get("group_study", 0)

    math_pct = data.get("math_score", 0)
    read_pct = data.get("reading_score", 0)
    focus_pct = data.get("focus_score", 0)

    summary_paragraphs = [
        f"在{country}，许多{age}岁的{gender_label}正踏上充满好奇心的学习旅程。{visual_pct}% 的孩子展现出对视觉学习的强烈偏好，他们更容易被图片、色彩和故事激发兴趣；{audio_pct}% 倾向于听觉方式，例如通过讲解和对话吸收知识；而 {action_pct}% 的孩子则在动手中学习，喜欢操作、实验或参与游戏。这些数据并非只是统计数字，而是展现了孩子如何与世界建立联系。家长若能善用这些倾向，例如使用图像书、亲子讲故事或引导式游戏，将有助于孩子更自然地理解和记忆新知识。",
        f"进一步观察日常学习习惯，{review_pct}% 的孩子已经形成了每日复习的规律，这显示出令人欣慰的自律；而 {solo_pct}% 在独立学习时展现出不错的专注与主动性，是内在学习动机的体现。不过，小组学习的比例只有 {group_pct}% ，可能意味着他们在协作环境中仍感到拘谨或缺乏信心。此时，家长可以通过轻松的亲子讨论、小规模互动或鼓励表达，慢慢引导孩子在互动中建立自信，培养表达与合作能力。",
        f"在核心科目的能力方面，{math_pct}% 的孩子在数学领域展现出稳定的基础和思维能力；阅读理解则达到 {read_pct}% ，显示他们在语言理解和想象力方面有不错的表现；而专注力目前为 {focus_pct}% ，略显薄弱但具备可提升空间。通过建立规律、适当安排音乐或休息时间，并减少干扰源，可以逐步增强他们在学习过程中的专注与节奏感。",
        f"这份学习画像不仅仅是对当前状态的描述，更像是一面镜子，映照出孩子成长的节奏与情绪线索。在新加坡、马来西亚与台湾，越来越多家庭意识到教育不能只关注成绩，而是需要结合情绪支持、习惯养成与潜能发展。善于觉察并温柔引导，是父母赋予孩子最温暖的礼物。希望这份报告，能为您的陪伴提供一盏光。"
    ]

    return "\n\n".join(summary_paragraphs)

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    data = request.json
    data["age"] = compute_age(data)
    summary = generate_child_summary(data)

    labels = ["视觉学习", "听觉学习", "动觉学习"]
    values = [
        data.get("visual_learning", 0),
        data.get("auditory_learning", 0),
        data.get("kinesthetic_learning", 0)
    ]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title("学习偏好分析")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    name = data.get("name", "无名")
    email_html = f"""
    <html><body style='font-family:sans-serif;color:#333'>
    <h2>🎯 新提交记录：</h2>
    <p>👤 <strong>姓名：</strong>{name}<br>
    🌍 <strong>国家：</strong>{data.get("country")}<br>
    🎂 <strong>年龄：</strong>{data.get("age")}<br>
    🧠 <strong>总结：</strong><br>{summary.replace("\n", "<br><br>")}</p>
    <img src="cid:chart" alt="分析图表"/>
    </body></html>
    """

    msg = MIMEMultipart('related')
    msg['Subject'] = f"📊 {name} 的学习分析报告"
    msg['From'] = SMTP_USERNAME
    msg['To'] = SMTP_USERNAME

    alt_part = MIMEMultipart('alternative')
    alt_part.attach(MIMEText(email_html, 'html', 'utf-8'))
    msg.attach(alt_part)

    img_part = MIMEText(base64.b64decode(chart_base64), 'base64', 'utf-8')
    img_part.add_header('Content-ID', '<chart>')
    img_part.add_header('Content-Disposition', 'inline', filename="chart.png")
    msg.attach(img_part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return jsonify({"summary": summary, "chart_base64": chart_base64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
