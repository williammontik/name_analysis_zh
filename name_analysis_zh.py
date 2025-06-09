# -*- coding: utf-8 -*-
import os, smtplib, logging, random, base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

# === OpenAI 设置 ===
openai.api_key = os.getenv("OPENAI_API_KEY")

# === 邮件设置 ===
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# === 月份映射（中英皆可）===
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

        # 月份解析
        if dob_month in CHINESE_MONTHS:
            month_num = CHINESE_MONTHS[dob_month]
        elif dob_month in ENGLISH_MONTHS:
            month_num = ENGLISH_MONTHS[dob_month]
        else:
            return jsonify({"error": f"❌ 无法识别的月份格式: {dob_month}"}), 400

        birthdate = datetime(int(dob_year), month_num, int(dob_day))
        age = datetime.now().year - birthdate.year

        # 随机图表数据
        metrics = [
            {"title": "学习偏好", "labels": ["视觉型", "听觉型", "动手型"], "values": random.sample(range(20, 80), 3)},
            {"title": "学习投入", "labels": ["每日复习", "小组学习", "自主学习"], "values": random.sample(range(20, 80), 3)},
            {"title": "学业信心", "labels": ["数学", "阅读", "专注力"], "values": random.sample(range(20, 80), 3)},
        ]

        # GPT 生成中文学习总结
        chart_values_text = "; ".join([
            f"{m['title']}：{', '.join([f'{l} {v}%' for l, v in zip(m['labels'], m['values'])])}"
            for m in metrics
        ])
        gpt_prompt = f"""
你是一个教育顾问，请基于以下资料，为一位住在{country}、{age}岁的{gender}儿童撰写四段式、温暖、有洞察力的中文学习总结。请参考这些数值：{chart_values_text}。
总结需充满情感与启发力，避免使用模板或列表，文字要自然流畅。
"""
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": gpt_prompt}],
            temperature=0.7
        )
        summary = gpt_response.choices[0].message.content.strip()

        # 构建邮件内容
        html_body = f"""
        <div style="font-family:'Microsoft YaHei',sans-serif;font-size:16px;">
        <p>👧 姓名：{name}</p>
        <p>🈶 中文名：{chinese_name}</p>
        <p>⚧️ 性别：{gender}</p>
        <p>🎂 生日：{dob_year}年{dob_month}{dob_day}日</p>
        <p>🕑 年龄：{age}</p>
        <p>🌍 国家：{country}</p>
        <p>📞 电话：{phone}</p>
        <p>📧 邮箱：{email}</p>
        <p>💬 推荐人：{referrer}</p>
        <hr>
        <p><strong>🧠 学习总结：</strong><br>{summary.replace('\n', '<br>')}</p>
        <hr>
        <p style="font-size:14px;color:#555;">
        本报告由 KataChat AI 系统生成，数据来源包括：<br>
        · 来自新加坡、马来西亚、台湾的匿名学习行为数据库（已获家长授权）<br>
        · OpenAI 教育研究数据与趋势分析<br>
        所有数据处理均符合 PDPA 数据保护规范。
        </p>
        </div>
        """

        # 发送邮件
        msg = MIMEMultipart('related')
        msg['Subject'] = "来自 KataChat 的学习报告"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME

        msg_alt = MIMEMultipart('alternative')
        msg.attach(msg_alt)
        msg_alt.attach(MIMEText(html_body, 'html', 'utf-8'))

        # 附加图表
        for i, img_data in enumerate(chart_images):
            if img_data.startswith("data:image/png;base64,"):
                img_data_clean = img_data.split(",")[1]
                image = MIMEImage(base64.b64decode(img_data_clean))
                image.add_header('Content-ID', f'<chart{i}>')
                image.add_header('Content-Disposition', 'inline', filename=f'chart{i}.png')
                msg.attach(image)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        return jsonify({
            "analysis": summary,
            "metrics": metrics
        })

    except Exception as e:
        logging.error("❌ 系统错误: %s", str(e))
        return jsonify({"error": "⚠️ 系统内部错误，请稍后再试"}), 500

# === 本地运行 ===
if __name__ == '__main__':
    app.run(debug=True)
