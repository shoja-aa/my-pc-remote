import flet as ft
import requests
import json
import threading
import time

CHANNEL_NAME = "shoja_pc_control_9592" 
URL_SEND = f"https://ntfy.sh/{CHANNEL_NAME}"
URL_RECEIVE = f"https://ntfy.sh/{CHANNEL_NAME}/json"

def main(page: ft.Page):
    page.title = "کنترلر هوشمند و واقعی لپ‌تاپ"
    page.bgcolor = "#121214"
    page.window_width = 360
    page.window_height = 500

    status_label = ft.Text("🔄 آماده ارسال دستور...", size=14, color="#4dabf7")

    def send_command(cmd_text):
        try:
            status_label.value = f"⏳ در حال ارسال '{cmd_text}'..."
            status_label.color = "#ffd43b"
            page.update()
            requests.post(URL_SEND, data=cmd_text.encode('utf-8'), timeout=5)
        except:
            status_label.value = "❌ خطا در اتصال به اینترنت"
            status_label.color = "#ff6b6b"
            page.update()

    # شنود پاسخ‌های لپ‌تاپ از سرور ابری
    def listen_for_replies():
        while True:
            try:
                resp = requests.get(URL_RECEIVE, stream=True, timeout=60)
                for line in resp.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if data.get("event") == "message":
                            msg = data.get("message", "").strip()
                            # اگر پیام پاسخِ لپ‌تاپ بود، کادر برنامه را آپدیت کن
                            if msg.startswith("پاسخ:"):
                                status_label.value = msg.replace("پاسخ:", "").strip()
                                status_label.color = "#51cf66"
                                page.update()
            except:
                time.sleep(2)

    # راه اندازی سیستم شنود در پس‌زمینه اپلیکیشن
    threading.Thread(target=listen_for_replies, daemon=True).start()

    def create_custom_button(text_str, bg_color_hex, command_str):
        return ft.Container(
            content=ft.Text(text_str, size=15, color="white"),
            padding=12,
            bgcolor=bg_color_hex,
            border_radius=8,
            on_click=lambda _: send_command(command_str)
        )

    page.add(
        ft.Container(height=10),
        ft.Text("🖥️ کنترلر هوشمند رئیس", size=20, color="white"),
        ft.Text("اتصال ابری و دوطرفه از خارج از خانه", size=12, color="#868e96"),
        ft.Container(height=15),
        
        create_custom_button("🏓 بررسی وضعیت سیستم (Ping)", "#2c2e33", "ping"),
        ft.Container(height=5),
        create_custom_button("💤 ورود به حالت Hibernate", "#2c2e33", "hibernate"),
        ft.Container(height=5),
        create_custom_button("🛑 خاموش کردن لپ‌تاپ (Shutdown)", "#fa5252", "shutdown"),
        
        ft.Container(height=15),
        ft.Text("گزارش وضعیت لحظه‌ای سیستم:", size=11, color="#868e96"),
        ft.Container(height=5),
        
        ft.Container(
            content=status_label,
            padding=15,
            bgcolor="#1e1e24",
            border_radius=8,
            height=100
        )
    )

ft.app(target=main)