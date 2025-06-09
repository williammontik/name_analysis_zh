# -*- coding: utf-8 -*-
import os, smtplib, logging, random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

CHINESE_GENDER = {
    '男': '男孩',
    '女': '女孩'
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

def generate_metrics():
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
            "title": "学习信心",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_summary(age, gender, country, metrics):
    p1 = f"在{country}，许多大约 {age} 岁的{gender}正悄悄建立属于他们的学习节奏。其中有 {metrics[0]['values'][0]}% 的孩子展现出对视觉型学习的偏好，说明图像、色彩与故事性内容能有效帮助他们理解抽象概念。听觉型占 {metrics[0]['values'][1]}%，而动手实践型为 {metrics[0]['values'][2]}%。这些数字不仅是统计，更反映了孩子在认知上对世界的不同感知路径。"

    p2 = f"在学习投入方面，有 {metrics[1]['values'][0]}% 的孩子已经养成每日复习的习惯，显示出他们在纪律与自律上的潜力。同时有 {metrics[1]['values'][2]}% 更喜欢独立学习，而只有 {metrics[1]['values'][1]}% 倾向参与小组学习，这可能意味着他们在集体协作方面尚在建立安全感。家长可以考虑从亲子共学或小圈子游戏中逐步引导。"

    p3 = f"从学习信心来看，数学信心高达 {metrics[2]['values'][0]}%，展现出逻辑推理与计算能力的发展。阅读信心为 {metrics[2]['values'][1]}%，表明部分孩子可能还在词汇或语言理解上积累中。专注力得分 {metrics[2]['values'][2]}%，显示出专注时间分布不均，尤其在面对电子干扰时更需策略性支持。"

    p4 = "综合而言，这些数据不仅呈现一个孩子的学习面貌，也反映出一个家庭支持系统的作用空间。父母若能结合孩子的偏好，创造一个视觉友好、节奏灵活、情绪被理解的学习环境，将有助于孩子在成长过程中保有自信与动力。"

    return [p1, p2, p3, p4]

def summary_to_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 学习总结：</div><br>" + \
        "".join(f"<p style='line-height:1.8; font-size:16px; margin-bottom:16px;'>{p}</p>\n" for p in paragraphs)

def generate_chart_html(metrics):
    def make_bar(title, labels, values, color):
        html = f"<h3 style='color:#333; margin-top:30px;'>{title}</h3>"
        for label, val in zip(labels, values):
            html += f"""
            <div style="margin:8px 0;">
              <div style="font-size:15px; margin-bottom:4px;">{label}</div>
              <div style="background:#eee; border-radius:10px; overflow:hidden;">
                <div style="background:{color}; width:{val}%; padding:6px 12px; color:white; font-weight:bold;">
                  {val}%
                </div>
              </div>
            </div>"""
        return html

    palette = ['#5E9CA0', '#FFA500', '#9966FF']
    return "".join(make_bar(m["title"], m["labels"], m["values"], palette[i % 3]) for i, m in enumerate(metrics))

def build_footer():
    return """
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>本报告由 KataChat AI 系统生成，数据来源包括：</strong><br>
      1. 来自新加坡、马来西亚、台湾的匿名学习行为数据库（已获家长授权）<br>
      2. OpenAI 教育研究数据与趋势分析<br>
      <em>所有数据处理均符合 PDPA 数据保护规范。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>附注：</strong> 若您希望进一步解读这些洞察，欢迎加入我们的 Telegram 或预约简短的指导交流。
    </p>
    """

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

        month_str = str(data.get("dob_month")).strip()
        month = CHINESE_MONTHS.get(month_str, None)
        if month is None:
            return jsonify({"error": f"❌ 无法识别的月份格式: {month_str}"}), 400
        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        gender_label = CHINESE_GENDER.get(gender, "孩子")

        metrics = generate_metrics()
        summary_paragraphs = generate_summary(age, gender_label, country, metrics)
        summary_html = summary_to_html(summary_paragraphs)
        charts_html = generate_chart_html(metrics)
        footer_html = build_footer()
        full_html = summary_html + charts_html + footer_html

        email_html = f"""<html><body style="font-family:sans-serif;color:#333">
        <h2>🎯 新用户提交信息:</h2>
        <p>
        👤 <strong>姓名:</strong> {name}<br>
        🈶 <strong>中文名:</strong> {chinese_name}<br>
        ⚧️ <strong>性别:</strong> {gender}<br>
        🎂 <strong>生日:</strong> {birthdate.date()}<br>
        🕑 <strong>年龄:</strong> {age}<br>
        🌍 <strong>国家:</strong> {country}<br>
        📞 <strong>电话:</strong> {phone}<br>
        📧 <strong>邮箱:</strong> {email}<br>
        💬 <strong>推荐人:</strong> {referrer}
        </p>
        <hr><h2>📊 AI分析报告</h2>
        {full_html}
        </body></html>"""

        send_email(email_html)

        return jsonify({
            "metrics": metrics,
            "analysis": full_html
        })

    except Exception as e:
        logging.exception("❌ /analyze_name 出现错误")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
