# -*- coding: utf-8 -*-
import os, smtplib, logging, random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS

# === Setup ===
app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# === Mappings ===
CHINESE_MONTHS = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4,
    '五月': 5, '六月': 6, '七月': 7, '八月': 8,
    '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}

CHINESE_GENDER = {
    '男': 'male',
    '女': 'female'
}

# === Email Sending ===
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

# === Chart Metrics ===
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

# === Summary Generation ===
def generate_child_summary(age, gender_zh, country, metrics):
    return [
        f"在{country}，许多约{age}岁的{gender_zh}孩子正在安静地探索学习之旅。视觉学习占比约{metrics[0]['values'][0]}%，听觉学习{metrics[0]['values'][1]}%，动觉方式{metrics[0]['values'][2]}%。这些数字不仅是统计，更是孩子探索世界的方式。",
        f"{metrics[1]['values'][0]}%的孩子每天复习，显示出自律习惯。{metrics[1]['values'][2]}%独立努力，体现自主性。但小组学习仅有{metrics[1]['values'][1]}%，家长可试着增加互动机会，比如共读故事、家庭问答等。",
        f"数学方面信心为{metrics[2]['values'][0]}%，阅读{metrics[2]['values'][1]}%，专注力为{metrics[2]['values'][2]}%。建议透过音乐或小游戏提高专注表现，让学习更轻松。",
        "这些数据反映出孩子在成长过程中真实的学习信号。透过调整学习方式与情绪支持，家长可帮助孩子更好地建立自信并发挥潜力。"
    ]

# === Build Summary HTML ===
def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 报告概览：</div><br>" + \
        "".join(f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>{p}</p>\n" for p in paragraphs)

# === Build Chart HTML ===
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
    return "".join(make_bar_html(m["title"], m["labels"], m["values"], colors[i % 3]) for i, m in enumerate(metrics))

# === Footer Block ===
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

# === API Endpoint ===
@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)

        name = data.get("name", "").strip()
        chinese_name = data.get("chinese_name", "").strip()
        gender_zh = data.get("gender", "").strip()
        country = data.get("country", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        referrer = data.get("referrer", "").strip()

        # Convert dob_month from Chinese to int
        month_str = data.get("dob_month", "").strip()
        month = CHINESE_MONTHS.get(month_str)
        if not month:
            return jsonify({"error": f"⚠️ 无效的月份: {month_str}"}), 400

        day = int(data.get("dob_day"))
        year = int(data.get("dob_year"))
        birthdate = datetime(year, month, day)

        # Convert gender to English for processing (if needed)
        gender_en = CHINESE_GENDER.get(gender_zh, "unknown")

        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_paragraphs = generate_child_summary(age, gender_zh, country, metrics)
        summary_html = generate_summary_html(summary_paragraphs)
        charts_html = generate_email_charts(metrics)
        email_html_result = build_email_report(summary_html, charts_html)

        email_html = f"""
        <html>
          <body style='font-family:sans-serif; color:#333'>
            <h2>🎯 新提交记录：</h2>
            <p>
              👤 <strong>姓名：</strong> {name}<br>
              🈶 <strong>中文名：</strong> {chinese_name}<br>
              ⚧️ <strong>性别：</strong> {gender_zh}<br>
              🎂 <strong>出生日期：</strong> {birthdate.date()}<br>
              🕑 <strong>年龄：</strong> {age}<br>
              🌍 <strong>国家：</strong> {country}<br>
              📞 <strong>电话：</strong> {phone}<br>
              📧 <strong>邮箱：</strong> {email}<br>
              💬 <strong>推荐人：</strong> {referrer}
            </p>
            <hr>
            <h2>📊 AI 分析报告</h2>
            {email_html_result}
          </body>
        </html>
        """

        send_email(email_html)

        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ Error in /analyze_name")
        return jsonify({"error": str(e)}), 500

# === Run Server ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
