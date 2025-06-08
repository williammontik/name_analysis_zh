# -*- coding: utf-8 -*-
import os
import smtplib
import base64
import random
from io import BytesIO
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt
from openai import OpenAI

app = Flask(__name__)
CORS(app)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def compute_age(data):
    try:
        d, m, y = data.get("dob_day"), data.get("dob_month"), data.get("dob_year")
        month = int(m) if m.isdigit() else {"一月":1, "二月":2, "三月":3, "四月":4, "五月":5, "六月":6,
                                            "七月":7, "八月":8, "九月":9, "十月":10, "十一月":11, "十二月":12}[m]
        bd = datetime(int(y), month, int(d))
        today = datetime.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except:
        return None

def generate_chart():
    labels = ['视觉学习', '听觉学习', '动觉学习', '数学兴趣', '阅读兴趣', '专注力']
    values = [random.randint(40, 90) for _ in range(len(labels))]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1, str(height), ha='center', fontsize=10)
    plt.ylim(0, 100)
    plt.xticks(rotation=30)
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return buffer, values

def generate_child_summary(age, gender, country, chart_values):
    v, a, k, m, r, f = chart_values
    paragraphs = []

    if gender == "男":
        prefix = f"在{country}，许多大约{age}岁的男孩子正在踏上探索学习的旅程。"
    else:
        prefix = f"在{country}，许多大约{age}岁的女孩子正以独特的节奏展开她们的学习旅程。"

    # Paragraph 1 — learning styles
    paragraphs.append(
        f"{prefix}视觉学习占比约为{v}%，听觉学习为{a}%，动觉学习约{k}%。这些风格不仅是统计数据，更反映了孩子们如何与世界互动。当学习内容能通过图像、声音或动作被传达时，理解力和专注度往往显著提升。"
    )

    # Paragraph 2 — daily habits
    paragraphs.append(
        f"从日常习惯来看，大约{random.randint(40, 65)}%的孩子已经养成每天温习的好习惯，显示出早期的自律能力。同时，大约{random.randint(35, 60)}%展现出独立学习的倾向，而小组学习比例为{random.randint(25, 50)}%。这可能意味着他们更习惯安静的环境。家长可尝试以亲子阅读或小游戏方式引导，激发他们在互动中找到乐趣。"
    )

    # Paragraph 3 — subject strengths
    paragraphs.append(
        f"在核心科目方面，数学兴趣达{m}%，阅读兴趣为{r}%，专注力水平为{f}%。虽然专注力略低，但可以透过音乐背景、短时休息或规律安排提升学习节奏，帮助他们更有效地吸收知识。"
    )

    # Paragraph 4 — emotional note
    paragraphs.append(
        f"这些数字背后藏着一个温柔的故事：这些孩子在默默努力，只是需要被理解和支持。新马台地区的家长若能结合视觉偏好与内在动机，选择平衡情绪与知识发展的资源，将能陪伴孩子更有信心地成长。"
    )

    return "\n\n".join(paragraphs)

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    data = request.json
    age = compute_age(data)
    gender = data.get("gender")
    country = data.get("country")
    name = data.get("name", "")
    chart_image, chart_values = generate_chart()
    summary = generate_child_summary(age, gender, country, chart_values)

    # ✅ FIXED: separate HTML-safe version
    summary_html = summary.replace("\n", "<br><br>")

    # Email with image
    msg = MIMEMultipart('related')
    msg['Subject'] = "📊 中文儿童报告"
    msg['From'] = SMTP_USERNAME
    msg['To'] = SMTP_USERNAME

    alt = MIMEMultipart('alternative')
    email_html = f"""
    <html><body style='font-family:sans-serif;color:#333'>
    <h2>🎯 新提交记录：</h2>
    <p>👤 <strong>姓名：</strong>{name}<br>
    🌍 <strong>国家：</strong>{country}<br>
    🎂 <strong>年龄：</strong>{age}<br>
    🧠 <strong>总结：</strong><br>{summary_html}</p>
    <img src="cid:chart" alt="分析图表"/>
    </body></html>
    """
    alt.attach(MIMEText(email_html, 'html', 'utf-8'))
    msg.attach(alt)

    img = MIMEImage(chart_image.read(), _subtype='png')
    img.add_header('Content-ID', '<chart>')
    msg.attach(img)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, SMTP_USERNAME, msg.as_string())

    return jsonify({
        "title": "🎉 全球 AI 分析：",
        "summary": summary
    })

if __name__ == "__main__":
    app.run(debug=True)
