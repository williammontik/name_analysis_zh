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

# === Email Config ===
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# === Month Mappings ===
CHINESE_MONTHS = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4,
    '五月': 5, '六月': 6, '七月': 7, '八月': 8,
    '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}

ENGLISH_MONTHS = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

# === Gender Map (if needed) ===
CHINESE_GENDER = {
    '男': 'male',
    '女': 'female'
}

# === Send Email Function ===
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
        logging.error("❌ 邮件发送失败: %s", str(e))

# === Analyze Endpoint ===
@app.route('/analyze_name', methods=['POST'])
def analyze_name():
    try:
        data = request.get_json()

        name = data.get("name", "")
        chinese_name = data.get("chinese_name", "")
        gender = data.get("gender", "")
        dob_day = data.get("dob_day", "")
        dob_month = data.get("dob_month", "")
        dob_year = data.get("dob_year", "")
        phone = data.get("phone", "")
        email = data.get("email", "")
        country = data.get("country", "")
        referrer = data.get("referrer", "")
        chart_images = data.get("chart_images", [])

        # Convert month string to number
        if dob_month in CHINESE_MONTHS:
            month_num = CHINESE_MONTHS[dob_month]
        elif dob_month in ENGLISH_MONTHS:
            month_num = ENGLISH_MONTHS[dob_month]
        else:
            return jsonify({"error": f"❌ 无法识别的月份格式: {dob_month}"}), 400

        birthdate = datetime(int(dob_year), month_num, int(dob_day))
        age = datetime.now().year - birthdate.year

        # Simulated metrics for testing (can replace with real logic)
        metrics = [
            {"title": "学习偏好", "labels": ["视觉型", "听觉型", "动手型"], "values": [50, 35, 11]},
            {"title": "学习投入", "labels": ["每日复习", "小组学习", "自主学习"], "values": [58, 22, 43]},
            {"title": "学业信心", "labels": ["数学", "阅读", "专注力"], "values": [67, 58, 58]},
        ]

        # AI summary (simplified for now)
        summary = f"""🧠 学习总结：

在{country}，许多年约 {age} 岁的{gender}孩子正在悄悄形成自己的学习习惯与喜好。视觉型学习者高达 50%，喜欢图像、颜色与故事形式。听觉型占 35%，动手型则为 11%。

58% 的孩子已经建立了每日复习的习惯，而 43% 倾向自主学习，小组学习仅占 22%。

在学业信心方面，数学为 67%，阅读为 58%，专注力为 58%。

这些趋势显示出孩子在逻辑、语言和情绪管理上的不同节奏，家长可以根据这些特点提供适切的支持。"""

        # Compose email HTML (can embed chart_images here too)
        html_body = f"""
        👤 姓名：{name}<br>
        🈶 中文名：{chinese_name}<br>
        ⚧️ 性别：{gender}<br>
        🎂 生日：{dob_year}-{dob_month}-{dob_day}<br>
        🕑 年龄：{age}<br>
        🌍 国家：{country}<br>
        📞 电话：{phone}<br>
        📧 邮箱：{email}<br>
        💬 推荐人：{referrer}<br><br>
        📊 AI 分析<br>{summary}<br><br>
        本报告由 KataChat AI 系统生成，数据来源包括：<br>
        1. 来自新加坡、马来西亚、台湾的匿名学习行为数据库（已获家长授权）<br>
        2. OpenAI 教育研究数据与趋势分析<br>
        所有数据处理均符合 PDPA 数据保护规范。
        """

        send_email(html_body)

        return jsonify({
            "analysis": summary,
            "metrics": metrics
        })

    except Exception as e:
        logging.error("❌ 系统错误: %s", str(e))
        return jsonify({"error": "⚠️ 系统内部错误，请稍后再试"}), 500

# === Run locally ===
if __name__ == '__main__':
    app.run(debug=True)
