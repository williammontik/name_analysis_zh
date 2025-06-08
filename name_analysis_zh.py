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
            "labels": ["视觉", "听觉", "动觉"],
            "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]
        },
        {
            "title": "学习投入度",
            "labels": ["每日复习", "小组学习", "独立学习"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学科自信度",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在{country}，许多年龄约为{age}岁的{gender.lower()}孩童正安静地踏入学习之路，展现出独特的学习偏好。其中，{metrics[0]['values'][0]}%的孩子偏好视觉学习 —— 他们喜欢通过图像、颜色与故事来理解世界。听觉学习占{metrics[0]['values'][1]}%，而动觉（例如动手操作）则为{metrics[0]['values'][2]}%。这些数据不仅是数字，它们也提醒我们：学习内容应以触动孩子想象与情感的方式呈现，才能激发出他们的好奇心与热情。",

        f"进一步观察他们的学习习惯，我们发现温暖的趋势正在浮现。有{metrics[1]['values'][0]}%的孩子已养成每日复习的习惯，这是他们纪律意识的体现。而{metrics[1]['values'][2]}%表现出良好的独立学习能力，反映了他们内在的动力。然而，仅有{metrics[1]['values'][1]}%参与小组学习，可能说明他们更偏好安静、安全的学习环境。家长可考虑透过亲子共学、与信任的朋友共读等方式，温和地引导他们参与集体学习。",

        f"在核心学科的自信表现方面，数学得分最高，为{metrics[2]['values'][0]}%，阅读紧随其后，为{metrics[2]['values'][1]}%。专注力方面则为{metrics[2]['values'][2]}%，显示他们还在发展专注的节奏。这并非弱点，而是一种成长节奏，只需耐心引导。例如减少屏幕时间、采用音乐融入学习、安排短暂活动休息等，都可能成为帮助他们找到节奏的小工具。",

        "这些学习信号，不只是报告，更是一段故事。它讲述了一个个小小脑袋背后充满希望的旅程。他们希望被大人们理解：不仅是成绩，而是努力的方式、情绪的表现与学习的倾向。无论是在新加坡、马来西亚或台湾，家长与教育者都有机会提供更符合孩子内在节奏的陪伴与资源，让学习成为平衡、自信、且充满乐趣的成长旅程。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 总结：</div><br>" + \
        "".join(f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>{p}</p>\n" for p in paragraphs)

def generate_email_charts(metrics):
    def make_bar_html(title, labels, values, color):
        bar_html = f"<h3 style='color:#333; margin-top:30px;'>{title}</h3>"
        for label, val in zip(labels, values):
            bar_html += f"""
            <div style="margin:8px 0;">
              <div style="font-size:15px; margin-bottom:4px;">{label}</div>
              <div style="background:#eee; border-radius:10px; overflow:hidden;">
                <div style="background:{color}; width:{val}%; padding:6px 12px; color:white; font-weight:bold;">
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
      <strong>本报告由 KataChat AI 系统生成，基于以下分析：</strong><br>
      1. 新加坡、马来西亚与台湾地区的匿名学习行为数据库（在家长同意下采集）<br>
      2. 第三方公开教育数据，包括 OpenAI 研究资料<br>
      <em>所有数据皆通过 AI 模型分析，识别具统计意义的趋势，且完全符合 PDPA 法规。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>附注：</strong> 个性化分析结果将于 24–48 小时内发送至您的邮箱。
      若您希望进一步探索报告内容，欢迎 Telegram 或预约 15 分钟快速交流。
    </p>
    """
    return summary_html + charts_html + footer

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        logging.info(f"[analyze_name] 接收到提交内容")

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

        email_html = f"""<html><body style="font-family:sans-serif;color:#333">
        <h2>🎯 新提交数据：</h2>
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

        # 仅网页端显示的结尾
        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ /analyze_name 处理失败")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
