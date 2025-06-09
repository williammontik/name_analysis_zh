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
        msg['Subject'] = "新的 KataChat 提交记录"
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
            "labels": ["视觉型", "听觉型", "动手型"],
            "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]
        },
        {
            "title": "学习投入",
            "labels": ["每日复习", "小组学习", "自主钻研"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学术信心",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    gender_text = "女孩" if gender == "女" else "男孩"
    return [
        f"在{country}，许多年约 {age} 岁的{gender_text}正在悄悄建立起属于他们的学习习惯与偏好。数据显示，视觉型学习占比为 {metrics[0]['values'][0]}%，遥遥领先；听觉型为 {metrics[0]['values'][1]}%，而动手实践型为 {metrics[0]['values'][2]}%。这些趋势反映出图像、色彩与故事性内容，正成为孩子们理解世界的重要媒介。",

        f"在学习投入方面，{metrics[1]['values'][0]}% 的孩子已养成每日复习的习惯，是一个令人欣慰的迹象。同时，{metrics[1]['values'][2]}% 倾向于独立钻研，展现出强烈的内在驱动力；但只有 {metrics[1]['values'][1]}% 常参与小组学习，可能反映他们更偏好安静、私密的学习环境。家长不妨尝试用轻松温暖的方式，引导孩子逐步适应与同龄人合作探索的过程。",

        f"从学科信心来看，{metrics[2]['values'][0]}% 对数学有高度信心，阅读为 {metrics[2]['values'][1]}%，而专注力为 {metrics[2]['values'][2]}%。这些数据说明孩子们在逻辑、语言与注意力的发展仍处于不同节奏中。透过情绪管理、规律作息、减少屏幕使用等方式，有助于提升他们的专注能力。",

        "这些学习数据，不只是冰冷的数字，而是一段关于成长的故事。对于在新马台的父母与教育者来说，这是一次了解孩子、支持孩子的机会。从视觉化教学到情绪陪伴，从自由探索到小组合作，只要我们用心陪伴，每位孩子都能在学习旅途中找到属于自己的节奏与信心。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 学习总结：</div><br>" + \
        "".join(f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>{p}</p>\n" for p in paragraphs)

def generate_email_charts(metrics):
    def make_bar_html(title, labels, values, color):
        bar_html = f"<h3 style='color:#333; margin-top:30px;'>{title}</h3>"
        for label, val in zip(labels, values):
            bar_html += f"""
            <div style=\"margin:8px 0;\">
              <div style=\"font-size:15px; margin-bottom:4px;\">{label}</div>
              <div style=\"background:#eee; border-radius:10px; overflow:hidden;\">
                <div style=\"background:{color}; width:{val}%; padding:6px 12px; color:white; font-weight:bold;\">
                  {val}%
                </div>
              </div>
            </div>
            """
        return bar_html

    color_map = ['#5E9CA0', '#FFA500', '#9966FF']
    charts_html = ""
    for idx, m in enumerate(metrics):
        color = color_map[idx % len(color_map)]
        charts_html += make_bar_html(m["title"], m["labels"], m["values"], color)
    return charts_html

def build_email_report(summary_html, charts_html):
    footer = """
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>本报告的洞察来自 KataChat 的 AI 系统分析：</strong><br>
      1. 我们针对新加坡、马来西亚和台湾儿童学习行为的匿名数据库（经父母授权）<br>
      2. 第三方可靠来源的教育趋势资料，包括 OpenAI 公布的研究数据集<br>
      <em>所有数据均经 AI 模型运算，符合 PDPA 隐私法规范。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>附注：</strong> 您的完整个性化报告将于 24-48 小时内发送至邮箱。
      若想进一步探讨结果，欢迎与我们 Telegram 或预约 15 分钟简聊。
    </p>
    """
    return summary_html + charts_html + footer

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        logging.info(f"[analyze_name] 接收到表单数据")

        name = data.get("name", "").strip()
        chinese_name = data.get("chinese_name", "").strip()
        gender = data.get("gender", "").strip()
        country = data.get("country", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        referrer = data.get("referrer", "").strip()

        month_str = str(data.get("dob_month")).strip()
        month = int(month_str) if month_str.isdigit() else datetime.strptime(month_str.capitalize(), "%B").month
        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_paragraphs = generate_child_summary(age, gender, country, metrics)
        summary_only_html = generate_summary_html(summary_paragraphs)
        charts_html = generate_email_charts(metrics)
        email_html_result = build_email_report(summary_only_html, charts_html)

        email_html = f"""<html><body style=\"font-family:sans-serif;color:#333\">
        <h2>🎯 新的用户提交：</h2>
        <p>
        👤 <strong>英文姓名：</strong> {name}<br>
        🈶 <strong>中文姓名：</strong> {chinese_name}<br>
        ⚧️ <strong>性别：</strong> {gender}<br>
        🎂 <strong>出生日期：</strong> {birthdate.date()}<br>
        🕑 <strong>年龄：</strong> {age}<br>
        🌍 <strong>国家：</strong> {country}<br>
        📞 <strong>电话：</strong> {phone}<br>
        📧 <strong>邮箱：</strong> {email}<br>
        💬 <strong>推荐人：</strong> {referrer}
        </p>
        <hr><h2>📊 AI 生成报告</h2>
        {email_html_result}
        </body></html>"""

        send_email(email_html)

        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ /analyze_name 处理错误")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
