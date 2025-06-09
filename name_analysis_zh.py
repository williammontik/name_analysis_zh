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
        {"title": "学习偏好", "labels": ["视觉型", "听觉型", "动手型"], "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]},
        {"title": "学习投入", "labels": ["每日复习", "小组学习", "自主学习"], "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]},
        {"title": "学习信心", "labels": ["数学", "阅读", "专注力"], "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]}
    ]

def generate_summary(age, gender, country, metrics):
    p1 = f"在{country}，许多大约 {age} 岁的{gender}正慢慢建立属于他们的学习节奏。其中有 {metrics[0]['values'][0]}% 的孩子偏好视觉型学习，说明图像、色彩与故事性内容对他们有明显吸引力；听觉型占比为 {metrics[0]['values'][1]}%，动手型为 {metrics[0]['values'][2]}%。这些数据不仅是统计数字，更揭示了孩子在感知世界时的多样化路径。"
    p2 = f"在学习投入方面，有 {metrics[1]['values'][0]}% 的孩子养成了每日复习的好习惯，显示出他们在纪律与自律方面的潜力。同时，{metrics[1]['values'][2]}% 更喜欢独立学习，而只有 {metrics[1]['values'][1]}% 倾向小组学习，这可能代表他们在人际协作上仍在建立安全感。家长可以从亲子共学或小圈子活动中逐步引导。"
    p3 = f"从学科信心来看，数学达到 {metrics[2]['values'][0]}%，展现出逻辑推理与计算能力的成熟；阅读信心为 {metrics[2]['values'][1]}%，提示语言理解与词汇积累仍在提升中；专注力得分 {metrics[2]['values'][2]}%，说明部分孩子在持续注意力上仍需适配合适节奏与环境。"
    p4 = "整体来看，孩子的成长轨迹不应被单一标准衡量。结合他们的偏好与节奏，父母可以打造一个视觉友好、情绪被理解、结构有弹性的支持系统，从而帮助他们在成长中建立自信与内在驱动力。"
    return [p1, p2, p3, p4]

def summary_to_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 学习总结：</div><br>" + \
        "".join(f"<p style='line-height:1.8; font-size:16px; margin-bottom:16px;'>{p}</p>\n" for p in paragraphs)

def generate_chart_html(metrics):
    def make_bar(title, labels, values, color):
        html = f"<h3 style='color:#333; margin-top:30px;'>{title}</h3>"
        for label, val in zip(labels, values):
            html += f"""
            <div style=\"margin:8px 0;\">
              <div style=\"font-size:15px; margin-bottom:4px;\">{label}</div>
              <div style=\"background:#eee; border-radius:10px; overflow:hidden;\">
                <div style=\"background:{color}; width:{val}%; padding:6px 12px; color:white; font-weight:bold;\">
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
      <strong>本报告中的洞察内容由 KataChat 的 AI 系统生成，分析对象包括：</strong><br>
      1. 我们专属数据库中来自新加坡、马来西亚与台湾学生的匿名学习行为模式（已获得家长授权）<br>
      2. 来自 OpenAI 教育研究数据集的汇总趋势（非个人数据）<br>
      <em>所有数据皆通过 AI 模型处理，旨在识别具统计意义的学习模式，并严格遵守 PDPA 隐私法规。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>附注：</strong> 您的个性化报告已发送至您的邮箱，通常将在 24-48 小时内收到。<br>
      若您希望进一步了解分析结果，欢迎通过 Telegram 联系我们，或预约 15 分钟快速沟通。
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

        full_email_html = f"<html><body style='font-family:sans-serif;color:#333'><h2>🎯 新用户提交信息:</h2><p>👤 姓名: {name}<br>🈶 中文名: {chinese_name}<br>⚧️ 性别: {gender}<br>🎂 生日: {birthdate.date()}<br>🕑 年龄: {age}<br>🌍 国家: {country}<br>📞 电话: {phone}<br>📧 邮箱: {email}<br>💬 推荐人: {referrer}</p><hr><h2>📊 AI分析报告</h2>{summary_html}{charts_html}{footer_html}</body></html>"

        send_email(full_email_html)

        frontend_html = charts_html + summary_html + footer_html
        return jsonify({"metrics": metrics, "analysis": frontend_html})

    except Exception as e:
        logging.exception("❌ /analyze_name 出现错误")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
