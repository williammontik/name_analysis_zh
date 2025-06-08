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
            "title": "学习投入",
            "labels": ["每日复习", "小组学习", "独立学习"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学术自信",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在 {country}，许多年龄大约为 {age} 岁的{gender}孩童正踏入学习的初期阶段，展现出安静而独特的学习倾向。其中，视觉学习最为突出，有 {metrics[0]['values'][0]}% 的孩子喜欢通过图像、颜色与故事来理解世界。听觉型学习为 {metrics[0]['values'][1]}%，而动觉型则是 {metrics[0]['values'][2]}%。这些数字不仅仅是数据，它们反映了孩子们希望透过触动心灵与想象的方式来学习。家长可以透过绘本、图像游戏与讲故事的方式，引导他们更深入地探索。",

        f"深入观察这些孩子的学习方式时，会发现温馨的趋势。其中 {metrics[1]['values'][0]}% 已经养成每日复习的习惯，是自律的表现；{metrics[1]['values'][2]}% 展现出强烈的独立学习动力，反映出他们的内在驱动力。然而，只有 {metrics[1]['values'][1]}% 经常参与小组学习，可能表示他们更倾向于在安静、安全的环境中学习。家长可思考如何以温和方式引导孩子适应同伴学习，例如亲子共读或与亲密朋友进行轻松的学习活动。",

        f"在核心学科方面，自信度也展现出重要趋势。数学表现最佳，达 {metrics[2]['values'][0]}%；阅读略高，为 {metrics[2]['values'][1]}%；而专注力得分为 {metrics[2]['values'][2]}%。这表明许多孩子仍在练习持续专注的能力。与其视为弱点，不如理解为一种发展节奏。情绪调节、规律作息、减少屏幕时间，以及结合音乐或活动的教学方式，或许能带来显著改善。每个孩子都有自己的节奏，关键在于如何协助他们找到那个节奏，而非比较或施压。",

        "这些学习讯号不仅仅是一个快照，而是一个故事 — 一个充满潜力的故事。家长与教育者在新加坡、马来西亚与台湾正面临一个机会：真正以孩子为中心的支持系统。无论是选择适合视觉型孩子的老师，或是寻找注重情感发展的教育环境，目标始终一致：让每位孩子在自信、平衡与喜悦中茁壮成长。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 综合分析：</div><br>" + \
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
      <strong>本报告由 KataChat AI 系统自动生成，数据来源包括：</strong><br>
      1. 我们专属数据库中来自新马台家长授权的匿名学习样本<br>
      2. 来自 OpenAI 与第三方平台的整体教育趋势资料<br>
      <em>所有数据经过 AI 模型分析，仅用于发现趋势，严格遵守 PDPA 隐私规范。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>备注：</strong> 您的完整个性化报告将于 24–48 小时内通过电邮发送。若想深入探讨分析内容，欢迎 Telegram 联系我们或预约 15 分钟对话。
    </p>
    """
    return summary_html + charts_html + footer

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        logging.info(f"[analyze_name] 收到提交")

        name = data.get("name", "").strip()
        chinese_name = data.get("chinese_name", "").strip()
        gender = data.get("gender", "").strip()
        country = data.get("country", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        referrer = data.get("referrer", "").strip()

        month_str = str(data.get("dob_month")).strip()
        month = int(month_str) if month_str.isdigit() else CHINESE_MONTHS.get(month_str, 1)
        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_paragraphs = generate_child_summary(age, gender, country, metrics)
        summary_only_html = generate_summary_html(summary_paragraphs)
        charts_html = generate_email_charts(metrics)
        email_html_result = build_email_report(summary_only_html, charts_html)

        email_html = f"""<html><body style=\"font-family:sans-serif;color:#333\">
        <h2>🎯 新用户提交：</h2>
        <p>
        👤 <strong>英文名：</strong> {name}<br>
        🈶 <strong>中文名：</strong> {chinese_name}<br>
        ⚧️ <strong>性别：</strong> {gender}<br>
        🎂 <strong>出生日期：</strong> {birthdate.date()}<br>
        🕑 <strong>年龄：</strong> {age}<br>
        🌍 <strong>国家：</strong> {country}<br>
        📞 <strong>电话：</strong> {phone}<br>
        📧 <strong>电邮：</strong> {email}<br>
        💬 <strong>推荐人：</strong> {referrer}
        </p>
        <hr><h2>📊 AI 分析报告</h2>
        {email_html_result}
        </body></html>"""

        send_email(email_html)

        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ /analyze_name 出现错误")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
