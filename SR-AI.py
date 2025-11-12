import gradio
import google.generativeai as genai
import feedparser
import os
from newsplease import NewsPlease


genai.configure(api_key="GOOGLE_API_KEY")
# คีย์โมเดล gemini
# เข้าไปเอาคีย์ที่
# https://aistudio.google.com/api-keys

def New():
    print("กำลังเริ่มดึงข่าว")
    new = []
    try:
        feed_url = "https://www.thairath.co.th/rss/news" #ใส่เพิ่มได้ แต่ต้อง , คั่นก่อน
        feed = feedparser.parse(feed_url)
        for i , entry in enumerate(feed.entries[:3]):

            if hasattr(entry , 'link'):
                new_url = entry.link
                print(f"[{i+1}] กำลังอ่าน{new_url}")
                newmess = NewsPlease.from_url(new_url)

                if newmess and newmess.maintext:
                    summary_text = newmess.maintext[:500] + "..."
                    new.append(f"""
- หัวข้อ: {newmess.title}      
- ที่มา: {newmess.source_domain}
- เนื้อหา: {summary_text}
- ลิงค์: {new_url}
"""
                    )
                else:
                    new.append(f""" ไม่สามารถดึงเนื้อหาหลักได้ {newmess.title} จาก{new_url}""")
            return "\n".join(new)
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด {e}")
        return "เกิดปัญหาภายใน"

def model():
    model = genai.GenerativeModel('gemini-2.5-flash')
    return model

ai_model = model()

def program(message , history):
    print("ข้อความที่ได้รับมาคือ",message)
    data_new = New()

    prompt =f"""
คุณคือ นักข่าวมืออาชีพ หน้าที่ของคุณคือ บรรยายเนื้อหา ที่ได้มาให้น่าฟัง หากเป้นคำถามทั่วไปให้ตอบปกติ

**นี่คือข่าวที่คุณสามารถหยิบมาบรรยายได้ **
---
{data_new} 
---
"""
    chat = ai_model.start_chat(
        history=[
            {"role":"user","parts":prompt},
            {"role":"model","parts":["รับทราบครับ ผมจะใช้ข้อมูลนี้ในการตอบคำถาม"]}
        ]
    )
    for user, ai in history:
        chat.history.append({"role": "user" ,"parts":[user]}),
        chat.history.append({"role": "model" ,"parts":[ai]})
    
    try:
        answer = chat.send_message(message)
        return answer.text
    
    except Exception as e:
        print(f"ผิดพลาดจากโมเดล{e}")
        return(f"โค้ดส่วน chat พัง")

print("เรียกใช้งาน gadio")

ui = gradio.ChatInterface(
    fn = program,
    title =" 😎 AI นักข่าวจำลอง",
    description = " AI จะดึงเนื้อหาข่าว 3 อันล่าสุดมาตอบ"
)

ui.launch(share=False)

print("เริ่มต้นที่ http://127.0.0.1:7860/")