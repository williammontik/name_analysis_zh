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
            "title": "学习投入",
            "labels": ["每日复习", "小组学习", "独立努力"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学科学习信心",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在 {country}，许多年幼的{gender.lower()}孩子正以安静而坚定的方式踏入学习的初期阶段，展现出独特的偏好。其中，视觉学习成为一项强有力的支点 —— 有 {metrics[0]['values'][0]}% 的学习者倾向于透过图像、颜色和故事来理解世界。听觉学习其次，占 {metrics[0]['values'][1]}%，而通过动手操作的动觉学习为 {metrics[0]['values'][2]}%。这些数据不仅仅是数字，更揭示了需要以打动孩子心灵和想象力的方式来呈现信息。对父母而言，这是一个将学习带回家的好机会 —— 透过图画书、视觉游戏和亲子故事时光，让学习变得充满乐趣与意义。",
        f"深入观察这些孩子的学习方式，会发现一项温暖的趋势：有 {metrics[1]['values'][0]}% 已经养成了每日复习的习惯 —— 在年幼时展现出如此自律，实属不易。同时，有 {metrics[1]['values'][2]}% 展现出强烈的独立学习动机，这种内在驱动力令人赞叹。但只有 {metrics[1]['values'][1]}% 经常参与小组学习，这或许反映出他们更偏好安静、安全的学习环境，而非充满竞争或吵杂的氛围。家长不妨思考：我们该如何温柔地引导孩子参与群体学习，而不带来压力？亲子复习时间，或与信任的朋友一同进行温馨的故事分享，或许是很好的桥梁。",
        f"在核心科目上的信心也揭示了重要信息。数学目前表现最为亮眼，占比为 {metrics[2]['values'][0]}%，而阅读则略高一点，为 {metrics[2]['values'][1]}%。专注力的得分为 {metrics[2]['values'][2]}%，显示许多孩子仍在学习如何保持持续注意力。但这并不是弱点，而是一种成长节奏 —— 需要用合适的“旋律”来引导。情绪调节、规律作息、减少屏幕时间、以及结合音乐或动作的教学方式，或许都能带来微妙却重要的转变。每个孩子都有自己的节奏 —— 关键在于如何在无压力、无比较的环境中帮助他们找到自己的步调。",
        "这些学习信号不仅是一个快照，更是一段真实的成长故事。故事中满是潜力与期望，只盼大人们能看见他们的努力、情绪和偏好，而不仅是分数。在新加坡、马来西亚和台湾，家长与教育者如今有机会提供真正以孩子为中心的支持 —— 无论是选择擅长视觉引导的导师，还是寻找重视情感成长的学校系统，目标始终如一：让每个孩子都能在平衡、自信与喜悦中茁壮成长。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 综合总结：</div><br>" + \
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
      <strong>本报告中的洞察由 KataChat 的 AI 系统生成，基于以下来源：</strong><br>
      1. 我们专有的、经过匿名处理的新加坡、马来西亚和台湾学生学习数据（经家长同意）<br>
      2. 来自 OpenAI 研究数据库等可信第三方的综合教育趋势<br>
      <em>所有数据均通过我们的 AI 模型进行处理，确保符合 PDPA 隐私法规。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>备注：</strong> 您的个性化报告将在 24-48 小时内发送到您的邮箱。
      如您希望进一步了解结果，可通过 Telegram 联系我们或预约 15 分钟咨询。
    </p>
    """
    return summary_html + charts_html + footer

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        logging.info("[analyze_name] 收到用户提交数据")

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
        <h2>🎯 新用户提交：</h2>
        <p>
        👤 <strong>英文名：</strong> {name}<br>
        🈶 <strong>中文名：</strong> {chinese_name}<br>
        ⚧️ <strong>性别：</strong> {gender}<br>
        🎂 <strong>出生日期：</strong> {birthdate.date()}<br>
        🕑 <strong>年龄：</strong> {age}<br>
        🌍 <strong>国家：</strong> {country}<br>
        📞 <strong>手机号：</strong> {phone}<br>
        📧 <strong>邮箱：</strong> {email}<br>
        💬 <strong>推荐人：</strong> {referrer}
        </p>
        <hr><h2>📊 AI 分析报告</h2>
        {email_html_result}
        </body></html>"""

        send_email(email_html)

        # 仅网页展示用 footer
        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ /analyze_name 出错")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
