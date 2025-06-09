# -*- coding: utf-8 -*-
import os, smtplib, logging, random, base64
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import matplotlib.pyplot as plt
from io import BytesIO
from openai import OpenAI

# === Setup ===
app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    '男': 'male',
    '女': 'female'
}

def generate_chart(title, labels, values):
    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.bar(labels, values, color=['#5E9CA0', '#FF9F40', '#9966FF'])
    ax.set_title(title)
    ax.set_ylim(0, 100)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

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
        logging.error("❌ 邮件发送失败: %s", e)

@app.route('/analyze_name', methods=['POST'])
def analyze_name():
    try:
        data = request.json
        name = data.get("name", "")
        chinese_name = data.get("chinese_name", "")
        gender = data.get("gender", "")
        dob_day = int(data.get("dob_day"))
        dob_year = int(data.get("dob_year"))
        dob_month_raw = str(data.get("dob_month")).strip()

        if dob_month_raw.isdigit():
            dob_month = int(dob_month_raw)
        elif dob_month_raw in CHINESE_MONTHS:
            dob_month = CHINESE_MONTHS[dob_month_raw]
        else:
            raise ValueError(f"Invalid month format: {dob_month_raw}")

        birthdate = datetime(dob_year, dob_month, dob_day)
        age = datetime.now().year - dob_year

        learning_style = ["视觉型", "听觉型", "动手型"]
        style_values = random.sample(range(20, 90), 3)
        study_habits = ["每日复习", "小组学习", "独立学习"]
        habit_values = random.sample(range(20, 90), 3)
        confidence = ["数学", "阅读", "专注力"]
        conf_values = random.sample(range(20, 90), 3)

        charts = [
            {"title": "学习风格", "labels": learning_style, "values": style_values},
            {"title": "学习投入", "labels": study_habits, "values": habit_values},
            {"title": "学术信心", "labels": confidence, "values": conf_values},
        ]
        chart_imgs = [generate_chart(c["title"], c["labels"], c["values"]) for c in charts]

        full_prompt = f"""
以下是关于一位年龄约 {age} 岁的孩子在新加坡的学习倾向数据（中文）：

学习风格：
视觉型: {style_values[0]}%
听觉型: {style_values[1]}%
动手型: {style_values[2]}%

学习投入：
每日复习: {habit_values[0]}%
小组学习: {habit_values[1]}%
独立学习: {habit_values[2]}%

学术信心：
数学: {conf_values[0]}%
阅读: {conf_values[1]}%
专注力: {conf_values[2]}%

请根据这些趋势，为家长生成一段富有洞察力、结构清晰的 4 段文字总结，使用温暖、理解和专业的语气，像一篇文章，不要提到名字或“你的孩子”。
        """.strip()

        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
        )
        ai_text = chat_response.choices[0].message.content.strip()

        html = f"""
        <html><body>
        <h2>🧠 中文分析报告</h2>
        <p><b>英文名:</b> {name}<br>
        <b>中文名:</b> {chinese_name}<br>
        <b>性别:</b> {gender}<br>
        <b>生日:</b> {dob_year}年{dob_month}月{dob_day}日<br>
        <b>国家:</b> {data.get("country", "")}<br>
        <b>电话:</b> {data.get("phone", "")}<br>
        <b>电邮:</b> {data.get("email", "")}</p>
        <hr>
        <h3>📊 图表分析</h3>
        {"".join([f'<h4>{charts[i]["title"]}</h4><img src="data:image/png;base64,{chart_imgs[i]}" style="max-width:600px;"><br><br>' for i in range(3)])}
        <hr>
        <h3>📝 AI 总结</h3>
        <p style="white-space: pre-wrap; font-size:16px;">{ai_text}</p>
        <hr><p style="color:#888;font-size:13px;">
        Insights generated by KataChatBot ·        Insights generated by KataChatBot \xb7 For educational support only ·        Insights generated by KataChatBot \xb7 For educational support only \xb7 Not medical advice</p>
        </body></html>
        """

        send_email(html)

        return jsonify({
            "metrics": charts,
            "analysis": ai_text
        })
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)
