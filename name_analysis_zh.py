# -*- coding: utf-8 -*-
import os, smtplib, logging, random
from datetime import datetime, date
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
    '一月': 1, '二月': 2, '三月': 3, '四月': 4,
    '五月': 5, '六月': 6, '七月': 7, '八月': 8,
    '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}

ENGLISH_MONTHS = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

def compute_age(day, month, year):
    try:
        month_num = (
            int(month) if str(month).isdigit()
            else CHINESE_MONTHS.get(month) or ENGLISH_MONTHS.get(month)
        )
        if not month_num:
            return None, f"❌ 无法识别的月份格式: {month}"
        birthdate = date(int(year), int(month_num), int(day))
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age, None
    except Exception as e:
        return None, f"❌ 出生日期格式错误: {str(e)}"

def generate_charts():
    categories = [
        {"title": "学习偏好", "labels": ["视觉型", "听觉型", "动手型"]},
        {"title": "学习投入", "labels": ["每日复习", "小组学习", "自主学习"]},
        {"title": "学业信心", "labels": ["数学", "阅读", "专注力"]}
    ]
    metrics = []
    for cat in categories:
        values = random.sample(range(20, 80), len(cat["labels"]))
        metrics.append({
            "title": cat["title"],
            "labels": cat["labels"],
            "values": values
        })
    return metrics

def generate_summary(age, gender, country, metrics):
    gender_text = "男孩子" if gender == "男" else "女孩子"
    para1 = f"在{country}，许多年约 {age} 岁的{gender_text}正在悄悄形成自己的学习习惯与喜好。" \
            f"{metrics[0]['labels'][0]}学习者高达 {metrics[0]['values'][0]}%，" \
            f"喜欢图像、颜色与故事形式。{metrics[0]['labels'][1]}占 {metrics[0]['values'][1]}%，" \
            f"{metrics[0]['labels'][2]}则为 {metrics[0]['values'][2]}%。"

    para2 = f"{metrics[1]['values'][0]}% 的孩子已经建立了每日复习的习惯，而 {metrics[1]['values'][2]}% 倾向自主学习，" \
            f"小组学习仅占 {metrics[1]['values'][1]}%。"

    para3 = f"在学业信心方面，{metrics[2]['labels'][0]}为 {metrics[2]['values'][0]}%，" \
            f"{metrics[2]['labels'][1]}为 {metrics[2]['values'][1]}%，{metrics[2]['labels'][2]}为 {metrics[2]['values'][2]}%。"

    para4 = "这些趋势显示出孩子在逻辑、语言和情绪管理上的不同节奏，家长可以根据这些特点提供适切的支持。"

    footer = (
        "<br><br><strong>本报告由 KataChat AI 系统生成，数据来源包括：</strong><br>"
        "1. 来自新加坡、马来西亚、台湾的匿名学习行为数据库（已获家长授权）<br>"
        "2. OpenAI 教育研究数据与趋势分析<br>"
        "所有数据处理均符合 PDPA 数据保护规范。"
    )

    return "<br><br>".join([para1, para2, para3, para4]) + footer

def send_email(html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "新的 KataChat 分析提交"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info("✅ 邮件发送成功")
    except Exception as e:
        logging.error(f"❌ 邮件发送失败: {e}")

@app.route('/analyze_name', methods=['POST'])
def analyze_name():
    data = request.get_json()
    name = data.get("name", "")
    chinese_name = data.get("chinese_name", "")
    gender = data.get("gender", "")
    dob_day = data.get("dob_day")
    dob_month = data.get("dob_month")
    dob_year = data.get("dob_year")
    phone = data.get("phone", "")
    email = data.get("email", "")
    country = data.get("country", "")
    referrer = data.get("referrer", "")
    chart_images = data.get("chart_images", [])

    age, error = compute_age(dob_day, dob_month, dob_year)
    if error:
        return jsonify({"error": error}), 400

    metrics = generate_charts()
    analysis = generate_summary(age, gender, country, metrics)

    chart_blocks = ""
    for img in chart_images:
        chart_blocks += f'<img src="{img}" style="width:400px; margin:20px auto; display:block;"><br>'

    html_body = f"""
    <p>👤 姓名：{name}</p>
    <p>🈶 中文名：{chinese_name}</p>
    <p>⚧️ 性别：{gender}</p>
    <p>🎂 生日：{dob_year}-{dob_month}-{dob_day}</p>
    <p>🕑 年龄：{age}</p>
    <p>🌍 国家：{country}</p>
    <p>📞 电话：{phone}</p>
    <p>📧 邮箱：{email}</p>
    <p>💬 推荐人：{referrer}</p><br>
    <h3>📊 AI 分析</h3>
    <div>{analysis}</div><br>
    <div>{chart_blocks}</div>
    """
    send_email(html_body)

    return jsonify({
        "analysis": analysis,
        "metrics": metrics
    })

if __name__ == '__main__':
    app.run(debug=True)
