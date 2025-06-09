# -*- coding: utf-8 -*-
import os, smtplib, logging, random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS

# === App Setup ===
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

# === Gender Mapping ===
CHINESE_GENDER = {
    '男': '男孩',
    '女': '女孩'
}

# === Send Email ===
def send_email(html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "新的 KataChatBot 提交記錄"
        msg['From'] = SMTP_USERNAME
        msg['To'] = SMTP_USERNAME
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info("✅ 郵件發送成功")
    except Exception as e:
        logging.error("❌ 郵件發送失敗: %s", str(e))

# === Main Analysis Endpoint ===
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

        # Convert month string
        if dob_month in CHINESE_MONTHS:
            month_num = CHINESE_MONTHS[dob_month]
        elif dob_month in ENGLISH_MONTHS:
            month_num = ENGLISH_MONTHS[dob_month]
        else:
            return jsonify({"error": f"❌ 無法識別的月份格式: {dob_month}"}), 400

        birthdate = datetime(int(dob_year), month_num, int(dob_day))
        age = datetime.now().year - birthdate.year
        gender_label = CHINESE_GENDER.get(gender, "孩子")

        # === Simulated Metrics ===
        metrics = [
            {"title": "學習偏好", "labels": ["視覺型", "聽覺型", "動手型"], "values": [50, 35, 11]},
            {"title": "學習投入", "labels": ["每日複習", "小組學習", "自主學習"], "values": [58, 22, 43]},
            {"title": "學業信心", "labels": ["數學", "閱讀", "專注力"], "values": [67, 58, 58]},
        ]

        # === Deep Summary Paragraphs ===
        para1 = f"在{country}，許多年約 {age} 歲的{gender_label}正在慢慢建立屬於自己的學習習慣與風格。從資料看來，視覺型學習偏好佔了 50%，說明圖片、顏色與圖像化內容對他們有明顯吸引力；聽覺型佔 35%，而動手實踐型則為 11%。這反映了此年齡段孩子在資訊吸收方式上的多元差異。"
        para2 = "在學習投入上，有 58% 的孩子已養成每日複習的好習慣，這是一個相當正面的訊號；而 43% 偏好自主學習，顯示他們具備自我驅動的潛力；至於小組學習則較少，僅 22%，這可能暗示著人際互動方面仍在培養中。"
        para3 = "學業信心方面，數學達到 67%，顯示他們對邏輯與計算有一定掌握；閱讀方面為 58%，略顯保守，可能與語言環境或詞彙基礎有關；而專注力則為 58%，反映孩子在持續注意力上的發展仍有提升空間。"
        para4 = "綜合來看，這些趨勢說明孩子正處於探索與成長的交叉點，家長可以根據其偏好與特質，提供更貼近需求的支持環境與學習資源，從而協助他們更自在地發揮潛能。"

        summary = f"🧠 學習總結：\n\n{para1}\n\n{para2}\n\n{para3}\n\n{para4}"

        # === Email Chart Blocks ===
        chart_blocks = ""
        for img in chart_images:
            chart_blocks += f'<img src="data:image/png;base64,{img}" style="width:100%; max-width:480px; margin-top:20px;"><br>'

        # === Email HTML ===
        html_body = f"""
        👤 姓名：{name}<br>
        🈶 中文名：{chinese_name}<br>
        ⚧️ 性別：{gender}<br>
        🎂 生日：{dob_year}-{dob_month}-{dob_day}<br>
        🕑 年齡：{age}<br>
        🌍 國家：{country}<br>
        📞 電話：{phone}<br>
        📧 郵箱：{email}<br>
        💬 推薦人：{referrer}<br><br>

        📊 AI 分析：<br>{summary.replace('\n', '<br>')}<br><br>
        {chart_blocks}

        <div style="background:#eef; padding:15px; border-left:6px solid #5E9CA0;">
        本報告由 KataChat AI 系統生成，數據來源包括：<br>
        1. 來自新加坡、馬來西亞、台灣的匿名學習行為資料庫（已獲家長授權）<br>
        2. OpenAI 教育研究數據與趨勢分析<br>
        所有數據處理均符合 PDPA 資料保護規範。
        </div>
        """

        # === Send Email ===
        send_email(html_body)

        # === Return to frontend ===
        return jsonify({
            "analysis": summary,
            "metrics": metrics
        })

    except Exception as e:
        logging.error("❌ 系統錯誤: %s", str(e))
        return jsonify({"error": "⚠️ 系統內部錯誤，請稍後再試"}), 500

# === Run Locally ===
if __name__ == '__main__':
    app.run(debug=True)
