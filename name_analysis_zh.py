# -*- coding: utf-8 -*-
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
import random

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
        msg['Subject'] = "新的员工表现分析提交"
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

@app.route('/boss_analyze', methods=['POST'])
def boss_analyze():
    try:
        data = request.get_json()
        
        # Extract all fields for boss analysis
        member_name = data.get("memberName", "")
        member_name_cn = data.get("memberNameCn", "")
        position = data.get("position", "")
        department = data.get("department", "")
        experience = data.get("experience", "")
        sector = data.get("sector", "")
        challenge = data.get("challenge", "")
        focus = data.get("focus", "")
        email = data.get("email", "")
        country = data.get("country", "")
        dob_day = data.get("dob_day", "")
        dob_month = data.get("dob_month", "")
        dob_year = data.get("dob_year", "")
        referrer = data.get("referrer", "")
        contact_number = data.get("contactNumber", "")
        
        # Generate metrics for boss/employee analysis (using random values for simplicity)
        metrics = [
            {
                "title": "沟通效率",
                "labels": ["团队沟通", "跨部门协作", "客户互动"],
                "values": [random.randint(70, 90), random.randint(65, 85), random.randint(50, 75)]
            },
            {
                "title": "领导力准备",
                "labels": ["决策能力", "团队激励", "战略思维"],
                "values": [random.randint(75, 95), random.randint(70, 90), random.randint(65, 85)]
            },
            {
                "title": "任务完成可靠性",
                "labels": ["按时完成", "质量标准", "问题解决"],
                "values": [random.randint(75, 95), random.randint(70, 90), random.randint(65, 85)]
            }
        ]
        
        # Generate Chinese analysis text for the report
        para1 = (
            f"在{country}，{sector}领域拥有{experience}年经验的{position}面临着独特的职场挑战。"
            f"数据显示，团队沟通效率达到{metrics[0]['values'][0]}%，而跨部门协作效率为{metrics[0]['values'][1]}%，"
            f"这表明在内部协调方面仍有提升空间。客户互动评分为{metrics[0]['values'][2]}%，"
            f"反映出在外部关系管理上可能需要更多关注。"
        )
        
        para2 = (
            f"在领导力方面，决策能力得分为{metrics[1]['values'][0]}%，表现出较强的判断力。"
            f"团队激励能力为{metrics[1]['values'][1]}%，战略思维达到{metrics[1]['values'][2]}%，"
            f"显示出您在管理团队和长远规划方面的优势。"
        )
        
        para3 = (
            f"任务完成可靠性方面，按时完成率为{metrics[2]['values'][0]}%，质量标准得分为{metrics[2]['values'][1]}%，"
            f"问题解决能力为{metrics[2]['values'][2]}%。这些数据表明您是一个可靠的专业人士，"
            f"在您关注的{focus}领域有着坚实的表现基础。"
        )
        
        para4 = (
            f"针对您提到的挑战「{challenge}」，我们建议：\n"
            f"1. 考虑参加领导力发展工作坊，进一步提升管理技能\n"
            f"2. 建立更系统的跨部门沟通机制\n"
            f"3. 在{focus}领域寻找行业导师或顾问\n"
            f"4. 定期进行360度反馈评估，了解团队需求\n"
            f"5. 关注行业最新趋势，保持竞争优势"
        )
        
        summary = f"🧠 专业表现分析：<br><br>{para1}<br><br>{para2}<br><br>{para3}<br><br>{para4}"
        
        # Generate email content
        html_body = f"""
        👤 员工姓名：{member_name}<br>
        🈶 中文名：{member_name_cn}<br>
        🏢 职位：{position}<br>
        📂 部门：{department}<br>
        🗓️ 从业年数：{experience}<br>
        📌 领域：{sector}<br>
        🌍 国家：{country}<br>
        📧 邮箱：{email}<br>
        💬 推荐人：{referrer}<br>
        📞 汇报对象：{contact_number}<br><br>
        
        ⚠️ 面临的挑战：{challenge}<br>
        🌟 关注方向：{focus}<br><br>
        
        📊 AI 分析：<br>{summary}
        """
        
        send_email(html_body)
        
        return jsonify({
            "analysis": summary,
            "metrics": metrics
        })
        
    except Exception as e:
        logging.error("❌ 系统错误: %s", str(e))
        return jsonify({"error": "⚠️ 系统内部错误，请稍后再试"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
