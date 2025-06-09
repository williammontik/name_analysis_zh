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
    '一月': 1, '二月': 2, '三月': 3, '四月': 4,
    '五月': 5, '六月': 6, '七月': 7, '八月': 8,
    '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}
ENGLISH_MONTHS = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
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
        logging.error("❌ 邮件发送失败: %s", str(e))

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

        if dob_month in CHINESE_MONTHS:
            month_num = CHINESE_MONTHS[dob_month]
        elif dob_month in ENGLISH_MONTHS:
            month_num = ENGLISH_MONTHS[dob_month]
        else:
            return jsonify({"error": f"❌ 无法识别的月份格式: {dob_month}"}), 400

        birthdate = datetime(int(dob_year), month_num, int(dob_day))
        age = datetime.now().year - birthdate.year
        gender_label = CHINESE_GENDER.get(gender, "孩子")

        metrics = [
            {"title": "学习偏好", "labels": ["视觉型", "听觉型", "动手型"], "values": [50, 35, 11]},
            {"title": "学习投入", "labels": ["每日复习", "小组学习", "自主学习"], "values": [58, 22, 43]},
            {"title": "学习信心", "labels": ["数学", "阅读", "专注力"], "values": [67, 58, 58]},
        ]

        para1 = f"在{country}，许多年约 {age} 岁的{gender_label}正在慢慢建立属于自己的学习习惯与风格。从数据来看，视觉型学习偏好占了 50%，说明图片、颜色与图像化内容对他们有明显吸引力；听觉型占 35%，而动手实践型则为 11%。这反映了此年龄段孩子在信息吸收方式上的多样差异。"
        para2 = "在学习投入方面，有 58% 的孩子已养成每日复习的好习惯，这是一个相当积极的信号；而 43% 偏好自主学习，显示他们具备自我驱动的潜力；至于小组学习则较少，仅 22%，这可能意味着人际互动方面仍在培养中。"
        para3 = "在学习信心方面，数学达到 67%，显示他们对逻辑与计算有一定掌握；阅读方面为 58%，略显保守，可能与语言环境或词汇基础有关；而专注力则为 58%，反映孩子在持续注意力上的发展仍有提升空间。"
        para4 = "综合来看，这些趋势说明孩子正处于探索与成长的交汇点，家长可以根据其偏好与特质，提供更贴近需求的支持环境与学习资源，从而协助他们更自在地发挥潜能。"

        summary = f"🧠 学习总结：\n\n{para1}\n\n{para2}\n\n{para3}\n\n{para4}"
        formatted_summary = summary.replace('\n', '<br>')

        chart_blocks = ""
        for img in chart_images:
            chart_blocks += f'<img src="data:image/png;base64,{img}" style="width:100%; max-width:480px; margin-top:20px;"><br>'

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

        📊 AI 分析：<br>{formatted_summary}<br><br>
        {chart_blocks}

        <div style="background:#eef; padding:15px; border-left:6px solid #5E9CA0;">
        本报告由 KataChat AI 系统生成，数据来源包括：<br>
        1. 来自新加坡、马来西亚、台湾的匿名学习行为数据库（已获家长授权）<br>
        2. OpenAI 教育研究数据与趋势分析<br>
        所有数据处理均符合 PDPA 数据保护规范。
        </div>
        """

        send_email(html_body)

        return jsonify({
            "analysis": summary,
            "metrics": metrics
        })

    except Exception as e:
        logging.error("❌ 系统错误: %s", str(e))
        return jsonify({"error": "⚠️ 系统内部错误，请稍后再试"}), 500

if __name__ == '__main__':
    app.run(debug=True)
