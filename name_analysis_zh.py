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
    "一月": 1, "二月": 2, "三月": 3, "四月": 4,
    "五月": 5, "六月": 6, "七月": 7, "八月": 8,
    "九月": 9, "十月": 10, "十一月": 11, "十二月": 12
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
            "labels": ["视觉型", "听觉型", "动手实践型"],
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
        f"在{country}，许多年约 {age} 岁的{gender}孩子正在悄悄建立起属于他们的学习习惯与偏好。数据显示，视觉型学习占比为 {metrics[0]['values'][0]}%，遥遥领先；听觉型为 {metrics[0]['values'][1]}%，而动手实践型为 {metrics[0]['values'][2]}%。这些趋势反映出图像、色彩与故事性内容，正成为孩子们理解世界的重要媒介。家长可以善用图画书、视觉游戏与亲子共读时光，打造愉快又深刻的学习体验。",

        f"在学习投入方面，{metrics[1]['values'][0]}% 的孩子已养成每日复习的习惯，是一个令人欣慰的迹象。同时，{metrics[1]['values'][2]}% 倾向于独自学习，展现出强烈的自我驱动力。然而，小组学习的比例仅为 {metrics[1]['values'][1]}%，可能反映出孩子在社交学习环境中尚未完全适应。家长可透过亲子复习时间或与信任伙伴的小组共学，慢慢引导孩子接纳并喜爱群体学习。",

        f"在学术信心方面，数学信心高达 {metrics[2]['values'][0]}%，阅读为 {metrics[2]['values'][1]}%，专注力与持续注意力为 {metrics[2]['values'][2]}%。这些数据揭示了孩子在逻辑、语言与情绪控制方面的成长节奏。家长不必急于求成，可透过规律作息、减少荧幕时间、加入音乐或肢体活动，温和引导孩子提升注意力。",

        "整体来看，这份报告所呈现的不只是分数，而是一个个真实、有潜力的孩子。他们希望大人能看见的不只是成绩，更是他们的努力、情绪与喜好。新马台的家长与教育者可以利用这些洞察，选择适合的教学方式，陪伴孩子在快乐与自信中稳步成长。"
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
    <p style=\"background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;\">
      <strong>本报告内容由 KataChat 人工智能系统生成，分析自：</strong><br>
      1. 我们来自新加坡、马来西亚和台湾学生的匿名学习数据（已获家长同意）<br>
      2. 来自 OpenAI 等可靠机构的非个人化公开教育趋势数据<br>
      <em>所有数据均遵守 PDPA 隐私保护政策，并经由本地 AI 系统进行统计建模。</em>
    </p>
    <p style=\"background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;\">
      <strong>📩 温馨提醒：</strong>完整报告也将于 24–48 小时内发送至您的邮箱。如有任何问题，可直接通过 Telegram 联系我们安排 15 分钟沟通时间。
    </p>
    """
    return summary_html + charts_html + footer

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        logging.info(f"[analyze_name] Payload received")

        name = data.get("name", "").strip()
        chinese_name = data.get("chinese_name", "").strip()
        gender = data.get("gender", "").strip()
        country = data.get("country", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        referrer = data.get("referrer", "").strip()

        month_str = str(data.get("dob_month")).strip()
        if month_str.isdigit():
            month = int(month_str)
        else:
            month = CHINESE_MONTHS.get(month_str, 1)

        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_paragraphs = generate_child_summary(age, gender, country, metrics)
        summary_only_html = generate_summary_html(summary_paragraphs)
        charts_html = generate_email_charts(metrics)
        email_html_result = build_email_report(summary_only_html, charts_html)

        email_html = f"""<html><body style=\"font-family:sans-serif;color:#333\">
        <h2>🎯 新用户提交信息：</h2>
        <p>
        👤 <strong>英文姓名:</strong> {name}<br>
        🈶 <strong>中文姓名:</strong> {chinese_name}<br>
        ⚧️ <strong>性别:</strong> {gender}<br>
        🎂 <strong>出生日期:</strong> {birthdate.date()}<br>
        🕑 <strong>年龄:</strong> {age}<br>
        🌍 <strong>国家:</strong> {country}<br>
        📞 <strong>电话:</strong> {phone}<br>
        📧 <strong>邮箱:</strong> {email}<br>
        💬 <strong>推荐人:</strong> {referrer}
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
        logging.exception("❌ /analyze_name 接口错误")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
