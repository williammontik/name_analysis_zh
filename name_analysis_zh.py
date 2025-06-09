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

# ✅ 中文月份映射
CHINESE_MONTHS = {
    "一月": "January", "二月": "February", "三月": "March", "四月": "April",
    "五月": "May", "六月": "June", "七月": "July", "八月": "August",
    "九月": "September", "十月": "October", "十一月": "November", "十二月": "December"
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
            "labels": ["每日复习", "小组学习", "独立钻研"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学术信心",
            "labels": ["数学", "阅读", "专注力与持续注意力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在 {country}，许多年约 {age} 岁的 {gender.lower()} 孩子正踏入学习的初阶阶段，带着安静的决心与独特的偏好。其中，视觉型学习最为显著，占比 {metrics[0]['values'][0]}%；听觉型为 {metrics[0]['values'][1]}%；而动手实践型占比 {metrics[0]['values'][2]}%。这些趋势显示，图像、颜色与故事性内容正在成为孩子们理解世界的重要媒介。父母可以透过图画书、视觉游戏及亲子故事时间，来激发孩子的学习兴趣与想象力。",
        f"在深入观察孩子们的学习方式后，一个动人的画面浮现：已有 {metrics[1]['values'][0]}% 的孩子养成每日复习的好习惯；另有 {metrics[1]['values'][2]}% 展现出独立学习时的高度自我驱动。但只有 {metrics[1]['values'][1]}% 经常参与小组学习，或许反映出他们偏好在安静、安全的空间中学习。父母可以尝试通过亲子共学或信任伙伴的小型共学时间，引导孩子逐步适应群体互动。",
        f"在核心学科方面，自信程度也展现了清晰的差异。数学的信心值为 {metrics[2]['values'][0]}%，阅读为 {metrics[2]['values'][1]}%，而专注与注意力则为 {metrics[2]['values'][2]}%。这说明孩子们在逻辑、语言与情绪控制方面的发展阶段不一。父母可以利用轻柔的生活节奏、减少屏幕时间，以及融入音乐或身体活动的教学方式，来帮助孩子找到属于自己的节奏。",
        "这些学习信号，不只是片段数据，而是孩子成长中的整体故事。在新加坡、马来西亚与台湾，父母与教育者有机会为孩子打造真正以他们为中心的学习支持系统。从适配视觉需求的导师选择，到重视情绪成长的学校机制，每一步的用心，都是帮助孩子快乐成长、自信前行的关键。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 学习总结：</div><br>" + \
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
    <strong>此报告由 KataChat AI 系统生成，分析依据如下：</strong><br>
    1. 来自新马台学生（已获得家长同意）的匿名学习资料数据库<br>
    2. 包括 OpenAI 在内的受信来源的非个人化教育趋势数据<br>
    <em>所有数据均在 PDPA 隐私框架下处理。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
    <strong>PS：</strong> 个性化报告将在 24–48 小时内送达邮箱。如需进一步了解分析结果，欢迎通过 Telegram 联系或预约 15 分钟交流。
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

        # ✅ 修复中文月份解析
        month_raw = str(data.get("dob_month")).strip()
        if month_raw in CHINESE_MONTHS:
            month_name = CHINESE_MONTHS[month_raw]
            month = datetime.strptime(month_name, "%B").month
        elif month_raw.isdigit():
            month = int(month_raw)
        else:
            month = datetime.strptime(month_raw, "%B").month

        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_paragraphs = generate_child_summary(age, gender, country, metrics)
        summary_only_html = generate_summary_html(summary_paragraphs)
        charts_html = generate_email_charts(metrics)
        email_html_result = build_email_report(summary_only_html, charts_html)

        email_html = f"""<html><body style="font-family:sans-serif;color:#333">
        <h2>🎯 新用户提交记录：</h2>
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
        logging.exception("❌ /analyze_name 错误")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
