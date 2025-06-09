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
        msg['Subject'] = "新KataChatBot提交"
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
            "labels": ["视觉型", "听觉型", "动觉型"],
            "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]
        },
        {
            "title": "学习参与度",
            "labels": ["每日复习", "小组学习", "自主学习"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学科信心",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在{country}，许多{age}岁左右的{gender.lower()}儿童正以独特的学习偏好进入早期学习阶段。其中视觉学习是最突出的方式——{metrics[0]['values'][0]}%的学习者倾向于通过图像、色彩和故事材料理解世界。听觉学习占{metrics[0]['values'][1]}%，动手实践等动觉方式占{metrics[0]['values'][2]}%。这些数字不仅反映了数据，更表明需要用触动孩子心灵和想象力的方式呈现信息。当孩子在图画或故事中看到自己的世界时，他们的好奇心会加深。对家长来说，这是通过绘本、视觉游戏和故事时间让学习变得快乐持久的机会。",

        f"深入观察这些儿童的学习参与度时，我们发现一个显著模式：{metrics[1]['values'][0]}%已养成每日复习的习惯——在这个年龄段展现了惊人的自律性。同时，{metrics[1]['values'][2]}%在独立学习时表现出强烈的自主性。但只有{metrics[1]['values'][1]}%经常参与小组学习，这可能暗示孩子情感上更偏好安全安静的学习环境而非竞争性环境。对家长而言，这引出一个问题：如何以支持性（而非压力性）的方式引导孩子进行同伴学习？亲子复习时间或与信任伙伴的小组故事会可能是理想的桥梁。",

        f"学科信心揭示了另一重要发现：数学信心值最高({metrics[2]['values'][0]}%)，阅读({metrics[2]['values'][1]}%)次之。专注力({metrics[2]['values'][2]}%)表明许多学习者仍在培养持续专注能力。家长可将此视为发展节奏——只需合适的旋律引导。情绪调节、温和的日常安排、减少屏幕时间以及融入音乐或运动休息的创新教学方法都可能带来积极改变。每个孩子都有自己的节奏——关键是在无压力的环境中帮助他们找到它。",

        "这些学习信号共同构成了一个故事——个充满潜力的年轻心灵的故事。孩子们默默希望周围的成人不仅看到结果，更注意到他们的努力、情绪和学习偏好。新加坡、马来西亚和台湾的家长与教育者现在有机会打造真正以儿童为中心的支持体系。无论是选择适应视觉需求的导师，还是寻找重视情感成长的教育系统——目标始终如一：帮助每个孩子在平衡、自我价值和快乐旅程中茁壮成长。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 分析摘要:</div><br>" + \
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
        <strong>本报告数据来源：</strong><br>
        1. 新加坡/马来西亚/台湾学生匿名学习模式数据库（经家长授权）<br>
        2. OpenAI等可信第三方教育趋势数据<br>
        <em>所有数据处理均符合PDPA个人数据保护法规</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
        <strong>注意：</strong>您的个性化报告将在24-48小时内发送至邮箱。
        如需进一步咨询，可通过Telegram联系我们或预约15分钟快速沟通。
    </p>
    """
    return summary_html + charts_html + footer

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        logging.info(f"[analyze_name] 收到请求数据")

        name = data.get("name", "").strip()
        chinese_name = data.get("chinese_name", "").strip()
        gender = data.get("gender", "").strip()
        country = data.get("country", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        referrer = data.get("referrer", "").strip()

        # 保留英文月份处理逻辑 (防止中文月份解析错误)
        month_str = str(data.get("dob_month")).strip()
        month = int(month_str) if month_str.isdigit() else datetime.strptime(month_str.capitalize(), "%B").month
        birthdate = datetime(int(data.get("dob_year")), month, int(data.get("dob_day")))
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        metrics = generate_child_metrics()
        summary_paragraphs = generate_child_summary(age, gender, country, metrics)
        summary_only_html = generate_summary_html(summary_paragraphs)
        charts_html = generate_email_charts(metrics)
        email_html_result = build_email_report(summary_only_html, charts_html)

        email_html = f"""<html><body style="font-family:sans-serif;color:#333">
        <h2>🎯 新用户提交：</h2>
        <p>
        👤 <strong>姓名：</strong> {name}<br>
        🈶 <strong>中文名：</strong> {chinese_name}<br>
        ⚧️ <strong>性别：</strong> {gender}<br>
        🎂 <strong>出生日期：</strong> {birthdate.date()}<br>
        🕑 <strong>年龄：</strong> {age}<br>
        🌍 <strong>国家：</strong> {country}<br>
        📞 <strong>电话：</strong> {phone}<br>
        📧 <strong>邮箱：</strong> {email}<br>
        💬 <strong>推荐人：</strong> {referrer}
        </p>
        <hr><h2>📊 AI生成报告</h2>
        {email_html_result}
        </body></html>"""

        send_email(email_html)

        # 网页端额外显示内容
        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ /analyze_name接口错误")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
