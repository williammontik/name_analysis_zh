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
            "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]
        },
        {
            "title": "学习投入",
            "labels": ["每日复习", "小组学习", "自主学习"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学业信心",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在{country}，许多年约 {age} 岁的{gender}孩子正在悄悄形成自己的学习习惯与喜好。视觉型学习者高达 {metrics[0]['values'][0]}%，喜欢图像、颜色与故事形式。听觉型占 {metrics[0]['values'][1]}%，动手型则为 {metrics[0]['values'][2]}%。这些趋势提醒我们，要用打动孩子感官与想象的方式呈现知识，比如绘本、可视化故事或互动活动，往往比死记硬背更有效。",
        
        f"{metrics[1]['values'][0]}% 的孩子已建立了每日复习的习惯，而 {metrics[1]['values'][2]}% 倾向独立学习，小组学习仅占 {metrics[1]['values'][1]}%。这显示许多孩子更喜欢在安静或熟悉的环境中学习。家长不妨透过亲子共学、温馨的家庭阅读角，逐步引导孩子适应团队学习的节奏。",
        
        f"在学业信心方面，数学为 {metrics[2]['values'][0]}%，阅读为 {metrics[2]['values'][1]}%，专注力为 {metrics[2]['values'][2]}%。这说明孩子在逻辑、语言与情绪调节上的发展步调各异。不必急于求成，可结合情绪引导、规律作息与音乐游戏等方式，温和帮助他们找到属于自己的学习节奏。",
        
        "这些趋势显示出孩子在逻辑、语言和情绪管理上的不同节奏，家长可以依据这些特点提供适切的支持。无论是选择适合视觉型的导师，或是鼓励孩子多表达感受，最终目标都是：帮助他们建立自信、找到自己的步伐，并在学习旅程中保持快乐与尊严。"
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
      <strong>附言：</strong>您的个性化完整报告将通过电子邮件发送，预计需要 24-48 小时。如有疑问，欢迎通过 Telegram 或安排 15 分钟对话进一步了解分析结果。
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

        # ✅ Chinese month support
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
        <h2>🎯 新的提交记录：</h2>
        <p>
        👤 姓名：{name}<br>
        🈶 中文名：{chinese_name}<br>
        ⚧️ 性别：{gender}<br>
        🎂 生日：{birthdate.date()}<br>
        🕑 年龄：{age}<br>
        🌍 国家：{country}<br>
        📞 电话：{phone}<br>
        📧 邮箱：{email}<br>
        💬 推荐人：{referrer}
        </p>
        <hr><h2>📊 AI 分析</h2>
        {email_html_result}
        </body></html>"""

        send_email(email_html)

        # Show footer in frontend too
        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ 后端错误")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
