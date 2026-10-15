import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# إعداد بوت تليجرام
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# معرفات قناتك والقروب الخاصة بك
CHANNEL_USERNAME = "@shbin4"
GROUP_USERNAME = "@Libya_Tbadl1"

def check_sub(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        group_member = bot.get_chat_member(GROUP_USERNAME, user_id)
        
        valid_statuses = ['creator', 'administrator', 'member']
        is_in_channel = chat_member.status in valid_statuses
        is_in_group = group_member.status in valid_statuses
        
        if is_in_channel and is_in_group:
            return True
        return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if check_sub(user_id):
        bot.send_message(message.chat.id, "أهلاً بك يا غالي! أرسل رابط فيديو تيك توك الآن وسيتم تحميله بدون علامة مائية فوراً.")
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("انضمام للقناة 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
        markup.add(InlineKeyboardButton("انضمام للقروب 💬", url=f"https://t.me/{GROUP_USERNAME.replace('@', '')}"))
        markup.add(InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check"))
        
        bot.send_message(
            message.chat.id, 
            "عذراً، يجب عليك الانضمام إلى القناة والقروب أولاً لاستخدام البوت:\n\nبعد الانضمام اضغط على زر (تحقق من الاشتراك 👇)", 
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "check")
def callback_check(call):
    user_id = call.from_user.id
    try:
        if check_sub(user_id):
            bot.answer_callback_query(call.id, "تم التحقق بنجاح! ✅", show_alert=False)
            bot.send_message(call.message.chat.id, "ممتاز يا غالي! الآن أرسل رابط فيديو تيك توك لتحميله بدون علامة مائية.")
        else:
            bot.answer_callback_query(call.id, "عذراً، لم تشترك في القناة والقروب بعد!", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, "حدث خطأ بسيط، حاول مجدداً.", show_alert=True)

@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        bot.send_message(message.chat.id, "عذراً، يجب عليك الاشتراك في القناة والقروب أولاً لتتمكن من التحميل!")
        return

    msg = bot.send_message(message.chat.id, "جاري تحميل الفيديو بدون علامة مائية... ⏳")
    
    try:
        url = message.text.strip()
        # استخدام API الاحتياطي المضمون أكثر للروابط القصيرة
        api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(api_url, headers=headers).json()

        if response.get("code") == 0:
            data = response.get("data", {})
            # محاولة جلب الفيديو بجودة عالية HD أولاً، وإذا لم تتوفر يجلب العادي
            video_url = data.get("hdplay") or data.get("play")
            
            if video_url:
                if video_url.startswith('/'):
                    video_url = f"https://www.tikwm.com{video_url}"
                    
                bot.send_video(message.chat.id, video_url, caption="تم التحميل بنجاح بواسطة البوت ✨")
                bot.delete_message(message.chat.id, msg.message_id)
                return

        # في حال فشل الرابط الأول، نجرب api بديل سريع
        alt_api = f"https://tikwm.com/api/?url={url}"
        alt_response = requests.get(alt_api, headers=headers).json()
        if alt_response.get("code") == 0:
            video_url = alt_response["data"].get("play")
            if video_url:
                if video_url.startswith('/'):
                    video_url = f"https://www.tikwm.com{video_url}"
                bot.send_video(message.chat.id, video_url, caption="تم التحميل بنجاح بواسطة البوت ✨")
                bot.delete_message(message.chat.id, msg.message_id)
                return

        bot.edit_message_text("عذراً، تعذر جلب الفيديو. تأكد من أن الرابط عام وليس خاصاً وجرب رابطاً آخر.", message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text(f"حدث خطأ تقني أثناء التحميل، حاول مجدداً.", message.chat.id, msg.message_id)

# --- خادم ويب وهمي لكي يرضى موقع Render ولا يتوقف البوت ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def start_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    start_bot()
