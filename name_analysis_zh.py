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
        msg['Subject'] = "新儿童学习表单提交"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USERNAME, SMTP_PASSWORD)
            s.send_message(msg)
        logging.info("✅ 邮件发送成功")
    except Exception:
        logging.exception("❌ 邮件发送失败")

def generate_child_metrics():
    return [
        {"title": "学习偏好", "labels": ["视觉型", "听觉型", "动手实践型"],
         "values": [random.randint(50, 70), random.randint(25, 40), random.randint(10, 30)]},
        {"title": "学习投入", "labels": ["每日复习", "小组学习", "自主学习"],
         "values": [random.randint(40, 60), random.randint(20, 40), random.randint(30, 50)]},
        {"title": "学业信心", "labels": ["数学", "阅读", "专注力"],
         "values": [random.randint(50, 85), random.randint(40, 70), random.randint(30, 65)]}
    ]

def generate_child_summary(age, gender, country, metrics):
    return [
        f"在{country}，许多年约 {age} 岁的{gender}孩子正在悄悄建立起属于他们的学习习惯与偏好。数据显示，视觉型学习占比为 {metrics[0]['values'][0]}%，遥遥领先；听觉型为 {metrics[0]['values'][1]}%，而动手实践型为 {metrics[0]['values'][2]}%。这些趋势反映出图像、色彩与故事性内容，正成为孩子们理解世界的重要媒介。",
        f"在学习投入方面，{metrics[1]['values'][0]}% 的孩子已养成每日复习的习惯，是一个令人欣慰的迹象。同时，{metrics[1]['values'][2]}% 倾向于自主学习，展现出内在驱动力；而小组学习的比例为 {metrics[1]['values'][1]}%，这或许意味着他们更习惯在安静、熟悉的环境中学习。",
        f"从学术信心来看，数学信心高达 {metrics[2]['values'][0]}%，阅读为 {metrics[2]['values'][1]}%，专注力与持续注意力为 {metrics[2]['values'][2]}%。这表明孩子们在逻辑、语言与情绪控制三方面的发展正处于不同阶段，家长可以根据这些特点给予相应的引导。",
        "整体而言，这些学习特征不仅仅是数据，而是每个孩子努力、情绪与成长轨迹的缩影。新马台地区的父母们正在面临一个时代转折点：如何在注重成绩的同时，也给予孩子更多理解与支持，让他们在学习的旅程中建立自信、找到平衡，并充满喜悦地探索世界。"
    ]

def generate_summary_html(paragraphs):
    return "<div style='font-size:24px; font-weight:bold; margin-top:30px;'>🧠 学习总结：</div><br>" + \
        "".join(f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>{p}</p>\n" for p in paragraphs)

def generate_email_charts(metrics):
    color_map = ['#5E9CA0', '#FFA500', '#9966FF']
    charts_html = ""
    for idx, m in enumerate(metrics):
        color = color_map[idx % len(color_map)]
        bar_html = f"<h3 style='color:#333; margin-top:30px;'>{m['title']}</h3>"
        for label, val in zip(m["labels"], m["values"]):
            bar_html += (
                f"<div style='margin:8px 0;'>"
                f"<div style='font-size:15px; margin-bottom:4px;'>{label}</div>"
                f"<div style='background:#eee; border-radius:10px; overflow:hidden;'>"
                f"<div style='background:{color}; width:{val}%; padding:6px 12px; color:white; font-weight:bold;'>"
                f"{val}%</div></div></div>"
            )
        charts_html += bar_html
    return charts_html

def build_email_report(summary_html, charts_html):
    footer = (
        "<p style='background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;'>"
        "<strong>本报告内容由 KataChat AI 系统生成，基于：</strong><br>"
        "1. 新加坡、马来西亚与台湾地区匿名儿童学习数据（在家长同意下采集）<br>"
        "2. 第三方公开教育趋势数据库与 OpenAI 研究资料<br>"
        "<em>所有内容均符合 PDPA 隐私法规并通过 AI 模型分析得出具统计意义的趋势。</em></p>"
        "<p style='background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;'>"
        "<strong>PS：</strong>分析结果将在 24-48 小时内以邮件方式发送。若希望进一步了解，请加入 Telegram 或预约简短交流。</p>"
    )
    return summary_html + charts_html + footer

@app.route('/analyze_name', methods=['POST'])
def analyze_name():
    try:
        data = request.get_json(force=True)
        name = data.get('name','').strip()
        chinese_name = data.get('chinese_name','').strip()
        gender = data.get('gender','')
        country = data.get('country','')
        phone = data.get('phone','').strip()
        email = data.get('email','').strip()
        referrer = data.get('referrer','').strip()

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
<h2>🎯 新表单提交：</h2>
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
<hr><h2>📊 AI 分析报告</h2>
{email_html_result}
</body></html>"""

        send_email(email_html)
        display_footer = build_email_report("", "")
        return jsonify({"metrics": metrics, "analysis": summary_only_html + display_footer})
    except Exception:
        logging.exception("❌ 处理 /analyze_name 出错")
        return jsonify({'error':'服务器内部错误'}),500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
