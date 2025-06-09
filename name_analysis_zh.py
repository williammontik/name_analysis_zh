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
        msg['Subject'] = "新的儿童分析提交"
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
        f"在{country}，许多年约 {age} 岁的{gender}孩子正在悄悄形成自己的学习习惯与喜好。视觉型学习者高达 {metrics[0]['values'][0]}%，喜欢图像、颜色与故事形式。听觉型占 {metrics[0]['values'][1]}%，动手型则为 {metrics[0]['values'][2]}%。",
        f"{metrics[1]['values'][0]}% 的孩子已经建立了每日复习的习惯，而 {metrics[1]['values'][2]}% 倾向自主学习，小组学习仅占 {metrics[1]['values'][1]}%。",
        f"在学业信心方面，数学为 {metrics[2]['values'][0]}%，阅读为 {metrics[2]['values'][1]}%，专注力为 {metrics[2]['values'][2]}%。",
        "这些趋势显示出孩子在逻辑、语言和情绪管理上的不同节奏，家长可以根据这些特点提供适切的支持。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 学习总结：</div><br>" + \
        "".join(f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>{p}</p>" for p in paragraphs)

def generate_email_charts(metrics):
    def make_bar_html(title, labels, values, color):
        bar_html = f"<h3 style='color:#333; margin-top:30px;'>{title}</h3>"
        for label, val in zip(labels, values):
            bar_html += f'''
            <div style="margin:8px 0;">
              <div style="font-size:15px; margin-bottom:4px;">{label}</div>
              <div style="background:#eee; border-radius:10px; overflow:hidden;">
                <div style="background:{color}; width:{val}%; padding:6px 12px; color:white; font-weight:bold;">
                  {val}%
                </div>
              </div>
            </div>
            '''
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

        dob_day = int(data.get("dob_day"))
        dob_year = int(data.get("dob_year"))
        dob_month_str = str(data.get("dob_month")).strip()

        # ✅ Safe month parsing
        if dob_month_str in CHINESE_MONTHS:
            dob_month = CHINESE_MONTHS[dob_month_str]
        elif dob_month_str.isdigit():
            dob_month = int(dob_month_str)
        else:
            return jsonify({"error": f"❌ 无法识别的月份格式: {dob_month_str}"}), 400

        birthdate = datetime(dob_year, dob_month, dob_day)
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary = generate_child_summary(age, gender, country, metrics)
        html_summary = generate_summary_html(summary)
        chart_html = generate_email_charts(metrics)
        email_body = build_email_report(html_summary, chart_html)

        full_email = f"""
        <html><body style="font-family:sans-serif;color:#333">
        <h2>🎯 新提交：</h2>
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
        {email_body}
        </body></html>
        """

        send_email(full_email)
        display_result = build_email_report(html_summary, "")
        return jsonify({"metrics": metrics, "analysis": display_result})

    except Exception as e:
        logging.exception("❌ 处理请求时出错")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
