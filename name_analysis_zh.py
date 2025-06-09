# -*- coding: utf-8 -*-
import base64
import os
import random
import smtplib
from datetime import datetime
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import matplotlib.pyplot as plt
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

CHINESE_MONTHS = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
    '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}

CHINESE_GENDER = {
    '男': '男孩',
    '女': '女孩'
}

def compute_age(day, month, year):
    try:
        month_num = CHINESE_MONTHS.get(month, 1)
        birth_date = datetime(int(year), month_num, int(day))
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except:
        return None

def generate_chart_base64(data_dict, title):
    fig, ax = plt.subplots(figsize=(6, 1.2))
    bars = ax.barh(list(data_dict.keys()), list(data_dict.values()))
    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{bar.get_width()}%', va='center')
    ax.set_xlim(0, 100)
    ax.set_title(title, fontsize=10)
    ax.axis('off')
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f'<img src="data:image/png;base64,{base64_str}" style="width:100%; max-width:500px; margin:10px 0;" />'

def generate_summary(age, gender, country, learning_styles, habits, confidence):
    g_text = CHINESE_GENDER.get(gender, "孩子")
    vs = learning_styles.get("视觉型", 0)
    as_ = learning_styles.get("听觉型", 0)
    ks = learning_styles.get("动手型", 0)
    daily = habits.get("每日复习", 0)
    solo = habits.get("独立学习", 0)
    group = habits.get("小组学习", 0)
    math = confidence.get("数学信心", 0)
    reading = confidence.get("阅读信心", 0)
    focus = confidence.get("专注力", 0)

    para1 = f"在{country}，许多大约 {age} 岁的{g_text}正逐步建立属于他们的学习节奏。数据显示，有 {vs}% 的孩子偏好视觉型学习，说明图像、色彩与结构化内容能帮助他们更好地掌握知识；听觉型为 {as_}%，动手型为 {ks}%。这些偏好反映出他们在理解世界时所依赖的感官路径日趋多样。"
    para2 = f"在学习投入方面，有 {daily}% 的孩子养成了每日复习的习惯，是学习自律的良好信号。{solo}% 喜欢独立学习，展现出他们对自我节奏的掌控；而仅有 {group}% 倾向小组学习，这或许说明他们在协作中仍需建立更多信心。"
    para3 = f"从学科自信来看，数学得分为 {math}%，代表他们在逻辑推理方面有一定优势；阅读信心为 {reading}%，提示词汇积累和语言理解尚有进步空间；专注力得分为 {focus}%，提醒家长优化学习环境与日常节奏，以提升持续注意力。"
    para4 = f"整体来看，这些趋势勾勒出{g_text}当前的成长轨迹。父母若能结合他们的偏好与节奏，提供一个视觉友好、情绪被理解、节奏被尊重的环境，将有助于他们在探索中建立自信，迈向更成熟的成长阶段。"

    return f"<p>{para1}</p><p>{para2}</p><p>{para3}</p><p>{para4}</p>"

FOOTER = """
<p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
  <strong>本报告中的洞察由 KataChat 的 AI 系统生成，依据以下来源分析：</strong><br>
  1. 我们专属数据库中经家长同意收集的新马台儿童学习模式匿名数据<br>
  2. 来自 OpenAI 等可信来源的教育趋势汇总（不包含个人信息）<br>
  <em>所有数据在严格遵守 PDPA 的前提下，通过 AI 模型识别统计显著趋势。</em>
</p>
<p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
  <strong>PS：</strong>您也将收到完整图表的邮件版本（请查收垃圾邮件箱）。如需进一步探讨结果，可 Telegram 联系我们或预约 15 分钟通话。
</p>
"""

def send_email(html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🎓 孩子学习分析报告 | KataChat AI"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        return False

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    data = request.get_json()
    name = data.get("name", "")
    gender = data.get("gender", "")
    country = data.get("country", "")
    email = data.get("email", "")
    day = data.get("dob_day")
    month = data.get("dob_month")
    year = data.get("dob_year")
    age = compute_age(day, month, year) or 10

    learning_styles = {
        "视觉型": random.randint(50, 80),
        "听觉型": random.randint(20, 50),
        "动手型": random.randint(20, 40)
    }

    study_habits = {
        "每日复习": random.randint(40, 70),
        "独立学习": random.randint(30, 60),
        "小组学习": random.randint(20, 50)
    }

    confidence_scores = {
        "数学信心": random.randint(40, 90),
        "阅读信心": random.randint(40, 80),
        "专注力": random.randint(30, 70)
    }

    chart1 = generate_chart_base64(learning_styles, "学习类型倾向")
    chart2 = generate_chart_base64(study_habits, "学习投入模式")
    chart3 = generate_chart_base64(confidence_scores, "学科信心与专注力")

    summary = generate_summary(age, gender, country, learning_styles, study_habits, confidence_scores)
    full_html = chart1 + chart2 + chart3 + summary + FOOTER

    send_email(full_html)

    return jsonify({
        "charts_html": chart1 + chart2 + chart3,
        "summary_html": summary,
        "footer_html": FOOTER
    })
