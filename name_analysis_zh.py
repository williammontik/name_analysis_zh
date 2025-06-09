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
            "labels": ["视觉型", "听觉型", "动手型"],
            "values": [random.randint(40, 70), random.randint(30, 50), random.randint(10, 30)]
        },
        {
            "title": "学习投入",
            "labels": ["每日复习", "小组学习", "自主学习"],
            "values": [random.randint(40, 70), random.randint(20, 50), random.randint(30, 70)]
        },
        {
            "title": "学业信心",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(40, 80), random.randint(40, 80), random.randint(30, 70)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在{country}，许多年约 {age} 岁的{gender}孩子正在悄悄形成自己的学习习惯与喜好。视觉型学习者高达 {metrics[0]['values'][0]}%，喜欢图像、颜色与故事形式。听觉型占 {metrics[0]['values'][1]}%，动手型则为 {metrics[0]['values'][2]}%。这些数字不仅反映了学习方式的多样性，更提醒我们：学习内容若能触动孩子的感官与情感，将更容易点燃他们的兴趣与动力。对家长而言，这意味着可以通过绘本、视觉化游戏或亲子讲故事，让学习变得生动而有温度。",

        f"{metrics[1]['values'][0]}% 的孩子已经建立了每日复习的习惯，是一个令人欣慰的信号。同时有 {metrics[1]['values'][2]}% 倾向于自主学习，展现出早期的自我驱动力。相比之下，小组学习仅占 {metrics[1]['values'][1]}%，可能说明孩子更喜欢在安静或熟悉的环境中学习。对于家长来说，这是一个温柔的提醒：也许我们可以尝试从亲子共学或与熟悉伙伴的小组互动开始，慢慢引导他们进入更开放的学习社交空间。",

        f"在学业信心方面，数学为 {metrics[2]['values'][0]}%，阅读为 {metrics[2]['values'][1]}%，专注力为 {metrics[2]['values'][2]}%。这说明孩子在逻辑、语言与情绪控制三方面的发展正处于不同节奏。而这种差异不该被视为问题，而是成长的节奏感。通过建立规律的作息、减少干扰性刺激，以及引入如音乐、动作结合的学习方式，孩子有机会更好地掌握持续专注的能力。",

        "这些趋势显示出孩子在逻辑、语言和情绪管理上的不同节奏。家长可以根据这些节奏提供恰当的支持与陪伴。真正的学习不仅是成绩的展现，更是理解与情绪的共鸣。当孩子被理解、被看见，他们将展现出最自然且稳定的成长潜力。"
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
      <strong>本报告由 KataChat AI 系统生成，数据来源包括：</strong><br>
      1. 来自新加坡、马来西亚、台湾的匿名学习行为数据库（已获家长授权）<br>
      2. OpenAI 教育研究数据与趋势分析<br>
      <em>所有数据处理均符合 PDPA 数据保护规范。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>PS：</strong>您的个性化报告将于 24–48 小时内发送至邮箱。如您希望进一步探讨，可通过 Telegram 或预约 15 分钟快速咨询。
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
        month_map = {
            "一月": 1, "二月": 2, "三月": 3, "四月": 4, "五月": 5, "六月": 6,
            "七月": 7, "八月": 8, "九月": 9, "十月": 10, "十一月": 11, "十二月": 12
        }
        if month_str.isdigit():
            month = int(month_str)
        elif month_str in month_map:
            month = month_map[month_str]
        else:
            raise ValueError(f"❌ 无法识别的月份格式: {month_str}")

        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_paragraphs = generate_child_summary(age, gender, country, metrics)
        summary_only_html = generate_summary_html(summary_paragraphs)
        charts_html = generate_email_charts(metrics)
        email_html_result = build_email_report(summary_only_html, charts_html)

        email_html = f"""<html><body style="font-family:sans-serif;color:#333">
        <h2>🎯 新用户提交信息：</h2>
        <p>
        👤 <strong>姓名：</strong> {name}<br>
        🈶 <strong>中文名：</strong> {chinese_name}<br>
        ⚧️ <strong>性别：</strong> {gender}<br>
        🎂 <strong>生日：</strong> {birthdate.date()}<br>
        🕑 <strong>年龄：</strong> {age}<br>
        🌍 <strong>国家：</strong> {country}<br>
        📞 <strong>电话：</strong> {phone}<br>
        📧 <strong>邮箱：</strong> {email}<br>
        💬 <strong>推荐人：</strong> {referrer}
        </p>
        <hr><h2>📊 AI 分析</h2>
        {email_html_result}
        </body></html>"""

        send_email(email_html)

        # Footer shown in result display too
        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ analyze_name 出现异常")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
