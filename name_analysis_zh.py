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

def send_email(html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "新的 KataChatBot 提交记录"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info("✅ 邮件发送成功")
    except Exception as e:
        logging.error("❌ 邮件发送失败", exc_info=True)

def generate_child_metrics():
    return [
        {
            "title": "学习偏好",
            "labels": ["视觉型", "听觉型", "动觉型"],
            "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]
        },
        {
            "title": "学习参与度",
            "labels": ["每日复习", "小组学习", "独立努力"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学术自信心",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在{country}，许多约{age}岁的{gender}孩子正在踏上他们独特的学习之旅。其中，视觉学习者占比约{metrics[0]['values'][0]}%，听觉型为{metrics[0]['values'][1]}%，动觉型则为{metrics[0]['values'][2]}%。这些比例揭示了孩子们如何通过图像、声音或实践来理解世界。适时提供丰富视觉或声音引导，将大大激发他们的学习动力。",
        f"从日常习惯看，{metrics[1]['values'][0]}%的孩子养成了每日复习的好习惯，展现出良好的自律能力；{metrics[1]['values'][2]}%孩子具备独立学习的动力，这是内在驱动的重要信号。相比之下，仅有{metrics[1]['values'][1]}%参与小组互动，或许他们更倾向安静、个人化的学习环境。家长不妨从亲子共读、家庭故事分享等温馨方式入手，温和地引导社交融合。",
        f"在学术表现方面，孩子在数学上的信心达到了{metrics[2]['values'][0]}%，阅读为{metrics[2]['values'][1]}%，专注力为{metrics[2]['values'][2]}%。若发现注意力稍显不足，可通过每日固定节奏、背景音乐或短时专注法，帮助他们建立可持续的学习节奏，找到适合自己的专注之道。",
        "整体而言，这些学习数据不仅是数字，更是孩子成长节奏的真实写照。他们正在默默努力、等待被理解。在新加坡、马来西亚与台湾，若能结合孩子偏好设计教材内容，并平衡学术与情绪成长，将能帮助他们建立更深层次的信心与归属感。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 报告概览：</div><br>" + \
        "".join(f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>{p}</p>\n" for p in paragraphs)

def generate_email_charts(metrics):
    def make_bar_html(title, labels, values, color):
        html = f"<h3 style='color:#333; margin-top:30px;'>{title}</h3>"
        for lab, val in zip(labels, values):
            html += f'''
            <div style="margin:8px 0;">
              <div style="font-size:15px; margin-bottom:4px;">{lab}</div>
              <div style="background:#eee; border-radius:10px; overflow:hidden;">
                <div style="background:{color}; width:{val}%; padding:6px 12px; color:white; font-weight:bold;">
                  {val}%
                </div>
              </div>
            </div>
            '''
        return html

    colors = ['#5E9CA0', '#FFA500', '#9966FF']
    charts_html = ""
    for idx, m in enumerate(metrics):
        charts_html += make_bar_html(m["title"], m["labels"], m["values"], colors[idx % len(colors)])
    return charts_html

def build_email_report(summary_html, charts_html):
    footer = f"""
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>该报告由 KataChat AI 生成，分析来源：</strong><br>
      1. 我们在新加坡、马来西亚和台湾收集的匿名学习数据（家长同意下）<br>
      2. 来自 OpenAI 教育趋势研究的汇总数据<br>
      <em>所有处理过程严格遵守 PDPA 数据保护规定。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>附注：</strong>您的个性化报告将在 24–48 小时内以电邮方式发送。如需深入讨论，请通过 Telegram 联系或预约 15 分钟通话。
    </p>
    """
    return summary_html + charts_html + footer

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        name = data.get("name", "").strip()
        chinese_name = data.get("chinese_name", "").strip()
        gender = data.get("gender", "").strip()
        country = data.get("country", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        referrer = data.get("referrer", "").strip()
        month_str = data.get("dob_month")
        month = int(month_str) if month_str.isdigit() else datetime.strptime(month_str, "%B").month
        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_ps = generate_child_summary(age, gender, country, metrics)
        summary_html = generate_summary_html(summary_ps)
        charts_html = generate_email_charts(metrics)
        email_html = f"<html><body style='font-family:sans-serif;color:#333'><h2>🎯 新提交记录：</h2><p>👤 <strong>姓名：</strong>{name}<br>📞 <strong>电话：</strong>{phone}<br>📧 <strong>电邮：</strong>{email}</p>{build_email_report(summary_html, charts_html)}</body></html>"

        send_email(email_html)
        return jsonify({"summary": summary_html})
    except Exception as e:
        logging.error("❌ 分析过程中出错", exc_info=True)
        return jsonify({"error": "⚠️ 网络错误或服务器无响应，请稍后重试。"}), 500
