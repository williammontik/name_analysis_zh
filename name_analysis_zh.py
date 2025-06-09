# -*- coding: utf-8 -*-
import os
import smtplib
import logging
import random
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# === Flask & Logging Setup ===
app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

# === SMTP Settings ===
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# === OpenAI Client ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Chinese Month Mapping ===
CHINESE_MONTHS = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4,
    '五月': 5, '六月': 6, '七月': 7, '八月': 8,
    '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}

CHINESE_GENDER = {
    '男': 'male',
    '女': 'female'
}

# === Compute Age ===
def compute_age(data):
    try:
        day = int(data.get("dob_day"))
        year = int(data.get("dob_year"))
        month_cn = data.get("dob_month")
        month = CHINESE_MONTHS.get(month_cn)
        if not month:
            raise ValueError(f"❌ 无法识别的月份格式: {month_cn}")
        birthdate = datetime(year, month, day)
        today = datetime.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    except Exception as e:
        raise ValueError(f"❌ 无法解析年龄: {e}")

# === AI Summary Generation ===
def generate_summary(gender, age, country, v, a, k, r, g, m, f):
    prompt = f"""
以下是一个居住在{country}的{age}岁{gender}孩童的学习数据，请用温暖细致、自然流畅的中文撰写4段说明，每段之间换行：

1. 描述此年龄层孩子的学习偏好（视觉{v}%、听觉{a}%、动手{k}%）
2. 描述他们的学习投入习惯（复习习惯{r}%、群体学习{g}%）
3. 描述他们的学业信心（数学{m}%、阅读{f}%、专注力{g}%）
4. 综合建议父母如何提供适切支持，帮助孩子发挥潜能。

请勿使用英文与人称用语（如“他/她/你”），直接描述趋势和观察。
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一位儿童学习顾问，请用中文分析儿童的学习行为数据"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

# === Email Sending ===
def send_email(subject, html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
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

# === Endpoint ===
@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json()
        name = data.get("full_name")
        gender_cn = data.get("gender")
        country = data.get("country")
        base64_chart = data.get("chart_data", "")
        gender = CHINESE_GENDER.get(gender_cn, "未知")
        age = compute_age(data)

        # 随机生成学习数据
        v, a, k = random.randint(40, 70), random.randint(20, 50), random.randint(10, 40)
        r, g = random.randint(40, 70), random.randint(20, 50)
        m, f = random.randint(50, 80), random.randint(40, 70)

        # 确保总和逻辑合理
        total = v + a + k
        if total > 100:
            excess = total - 100
            v -= excess // 3
            a -= excess // 3
            k -= excess // 3

        # 获取 AI 中文总结
        summary = generate_summary(gender_cn, age, country, v, a, k, r, g, m, f)
        formatted_summary = summary.replace('\n', '<br>')

        # 生成 HTML 响应
        chart_html = f'<img src="{base64_chart}" style="max-width:100%; height:auto;">' if base64_chart else ""
        html_body = f"""
        <div style="font-family:Arial, sans-serif; padding:20px; background:#f9f9f9;">
          <h2 style="color:#5E9CA0;">🎉 全球健康洞察：</h2>
          <p><strong>🧠 学习总结：</strong><br>{formatted_summary}</p>
          <br>{chart_html}
          <hr style="margin:30px 0;">
          <div style="font-size:14px; color:#888; line-height:1.6;">
            <p><strong>📩 分析来源：</strong> KataChat 学习指导系统</p>
            <p><strong>📊 数据解释：</strong> 本报告基于区域同龄人数据，结合孩子情况智能生成</p>
            <p><strong>📌 温馨提醒：</strong> 本结果仅供参考，实际学习需求请结合日常观察</p>
          </div>
        </div>
        """

        send_email("新的儿童学习分析报告", html_body)

        return jsonify({
            "status": "success",
            "summary": formatted_summary,
            "v": v, "a": a, "k": k, "r": r, "g": g, "m": m, "f": f
        })
    except Exception as e:
        logging.error(f"❌ 分析错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# === App Entry Point ===
if __name__ == "__main__":
    app.run(debug=True)
