import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- إعدادات التوكن والبوت ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# --- معرفات القناة والقروب للاشتراك الإجباري ---
CHANNEL_USERNAME = "@shbin4"
GROUP_USERNAME = "@Libya_Tbadl1"

# --- دالة التحقق من اشتراك المستخدم ---
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

# --- أمر /start ---
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if check_sub(user_id):
        bot.send_message(message.chat.id, "أهلاً بك يا غالي! 🌟\n\nأرسل رابط فيديو تيك توك الآن وسيتم تحميله بدون علامة مائية فوراً.")
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("انضمام للقناة 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
        markup.add(InlineKeyboardButton("انضمام للقروب 💬", url=f"https://t.me/{GROUP_USERNAME.replace('@', '')}"))
        markup.add(InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check"))
        
        bot.send_message(
            message.chat.id, 
            "عذراً يا غالي، يجب عليك الانضمام إلى القناة والقروب أولاً لاستخدام البوت:\n\nبعد الانضمام اضغط على زر (تحقق من الاشتراك 👇)", 
            reply_markup=markup
        )

# --- زر التحقق من الاشتراك ---
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

# --- استقبال وتحميل فيديوهات تيك توك بدون علامة مائية ---
@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    user_id = message.from_user.id
    
    if not check_sub(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("انضمام للقناة 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
        markup.add(InlineKeyboardButton("انضمام للقروب 💬", url=f"https://t.me/{GROUP_USERNAME.replace('@', '')}"))
        markup.add(InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check"))
        bot.send_message(message.chat.id, "عذراً، يجب عليك الاشتراك في القناة والقروب أولاً لتتمكن من التحميل!", reply_markup=markup)
        return

    msg = bot.send_message(message.chat.id, "جاري تحميل الفيديو بدون علامة مائية... ⏳")
    
    try:
        url = message.text.strip()
        api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(api_url, headers=headers, timeout=15)
        data_json = response.json()

        if data_json.get("code") == 0:
            video_data = data_json.get("data", {})
            video_url = video_data.get("hdplay") or video_data.get("play")
            
            if video_url:
                if video_url.startswith('/'):
                    video_url = f"https://www.tikwm.com{video_url}"
                    
                bot.send_video(message.chat.id, video_url, caption="✨ تم التحميل بنجاح بدون علامة مائية بواسطة البوت")
                bot.delete_message(message.chat.id, msg.message_id)
                return

        bot.edit_message_text("عذراً، تعذر جلب الفيديو. تأكد أن الرابط عام وصحيح وجرب رابطاً آخر.", message.chat.id, msg.message_id)
        
    except Exception as e:
        print(f"Download Error: {e}")
        bot.edit_message_text("حدث خطأ أثناء الاتصال بسيرفر التحميل، حاول مجدداً بعد قليل.", message.chat.id, msg.message_id)

# --- خادم الويب الوهمي (Flask) للـ Web Service ليظل البوت شغالاً مجاناً ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is active and running 24/7!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def start_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل سيرفر الفلاسك في الخلفية
    web_thread = Thread(target=run_web)
    web_thread.start()
    
    # تشغيل البوت الأساسي
    start_bot()
