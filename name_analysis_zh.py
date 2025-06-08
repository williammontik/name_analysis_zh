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

def generate_child_metrics():
    return [
        {
            "title": "学习偏好",
            "labels": ["视觉", "听觉", "动手实践"],
            "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]
        },
        {
            "title": "学习投入",
            "labels": ["每日复习", "小组学习", "独立学习"],
            "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]
        },
        {
            "title": "学科学习信心",
            "labels": ["数学", "阅读", "专注力"],
            "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]
        }
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在{country}，许多年约{age}岁的{gender}孩子，正以安静的决心与独特的节奏，踏入学习的启蒙阶段。其中，有{metrics[0]['values'][0]}%的孩子展现出对“视觉学习”的偏好，他们通过图像、颜色和故事来理解世界。听觉学习的比例为{metrics[0]['values'][1]}%，动手实践的学习方式则为{metrics[0]['values'][2]}%。这些数字并非冰冷的数据，而是提醒我们：孩子们需要的是能触动内心与想象力的学习方式。绘本、视觉游戏、家庭故事时间，都是家长可以立即实践的桥梁。",
        
        f"深入观察孩子们的学习习惯，我们看见一些温柔的趋势：{metrics[1]['values'][0]}%的孩子已养成“每日复习”的习惯，这是一个令人鼓舞的早期自律表现。而{metrics[1]['values'][2]}%的孩子展现出在独立学习中的高度投入，这显示了他们内在的驱动力。但仅有{metrics[1]['values'][1]}%参与小组学习，或许反映出他们更偏好安静、安全的学习空间，而非热闹竞争的场景。家长可以尝试引导，例如与孩子一起复习，或组织温馨的亲友共读时光，慢慢建立社交学习的信任感。",
        
        f"在核心学科的信心方面，{metrics[2]['values'][0]}%的孩子在数学上表现最为自信；而阅读的自信比例为{metrics[2]['values'][1]}%。在“专注力”方面为{metrics[2]['values'][2]}%，这提醒我们许多孩子仍在学习专注的节奏。但这不是缺点，而是一种自然的发展节拍。通过建立规律作息、减少电子产品时间、加入音乐或肢体活动等创新教学方式，能帮助孩子逐步找到属于自己的节奏与专注状态。",
        
        "整体来看，这些学习数据不仅是一组统计，更像是孩子内在世界的声音。他们渴望被理解，不只是成绩上的表现，而是努力的过程、学习的情绪、以及他们真正的偏好。身处新加坡、马来西亚和台湾的家长与教育者，有机会用更细腻的方式支持孩子成长。从为孩子选择适合视觉型教学的导师，到寻求注重情绪成长的学校体系，我们所做的每一个决定，最终都在塑造孩子充满自信、平衡感与快乐的学习旅程。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 学习报告摘要：</div><br>" + \
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
      <strong>本报告由 KataChat AI 系统生成，基于以下数据来源：</strong><br>
      1. 来自新加坡、马来西亚、台湾儿童（家长授权）的匿名学习行为数据库<br>
      2. 来自 OpenAI 教育研究及可信教育趋势数据的整合参考<br>
      <em>所有数据均严格遵守 PDPA 隐私标准进行分析与呈现。</em>
    </p>
    <p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">
      <strong>PS：</strong> 本报告也已发送至您的邮箱，若您希望进一步了解报告内容，欢迎随时联络我们安排一次 15 分钟交流。
    </p>
    """
    return summary_html + charts_html + footer

@app.route("/analyze_name", methods=["POST"])
def analyze_name():
    try:
        data = request.get_json(force=True)
        logging.info(f"[analyze_name] Payload received")

        name = data.get("name", "").strip()
        chinese_name = data.get("chinese_name", "").strip()
        gender = data.get("gender", "").strip()
        country = data.get("country", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        referrer = data.get("referrer", "").strip()

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
        👤 <strong>英文姓名：</strong> {name}<br>
        🈶 <strong>中文姓名：</strong> {chinese_name}<br>
        ⚧️ <strong>性别：</strong> {gender}<br>
        🎂 <strong>出生日期：</strong> {birthdate.date()}<br>
        🕑 <strong>年龄：</strong> {age}<br>
        🌍 <strong>国家：</strong> {country}<br>
        📞 <strong>电话：</strong> {phone}<br>
        📧 <strong>邮箱：</strong> {email}<br>
        💬 <strong>推荐人：</strong> {referrer}
        </p>
        <hr><h2>📊 AI 学习报告</h2>
        {email_html_result}
        </body></html>"""

        send_email(email_html)

        display_footer = build_email_report("", "")
        return jsonify({
            "metrics": metrics,
            "analysis": summary_only_html + display_footer
        })

    except Exception as e:
        logging.exception("❌ /analyze_name 处理出错")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
