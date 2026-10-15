import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# إعداد بوت تليجرام
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL_USERNAME = "@shbin4"  # استبدل بمعرف قناتك
GROUP_USERNAME = "@Libya_Tbadl1"      # استبدل بمعرف قروبك

def check_sub(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        group_member = bot.get_chat_member(GROUP_USERNAME, user_id)
        
        valid_statuses = ['creator', 'administrator', 'member']
        if chat_member.status in valid_statuses and group_member.status in valid_statuses:
            return True
        return False
    except Exception:
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
    if check_sub(user_id):
        bot.answer_callback_query(call.id, "تم التحقق بنجاح! ✅")
        bot.send_message(call.message.chat.id, "ممتاز! الآن أرسل رابط فيديو تيك توك لتحميله.")
    else:
        bot.answer_callback_query(call.id, "لم تشترك في القناة والقروب بعد!", show_alert=True)

@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        bot.send_message(message.chat.id, "عذراً، يجب عليك الاشتراك في القناة والقروب أولاً لتتمكن من التحميل!")
        return

    msg = bot.send_message(message.chat.id, "جاري تحميل الفيديو بدون علامة مائية... ⏳")
    
    try:
        url = message.text.strip()
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()

        if response.get("code") == 0:
            video_url = response["data"]["play"]
            bot.send_video(message.chat.id, video_url, caption="تم التحميل بنجاح بواسطة البوت ✨")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("عذراً، تعذر جلب الفيديو. تأكد من أن الرابط صحيح.", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("حدث خطأ أثناء تحميل الفيديو، حاول مجدداً.", message.chat.id, msg.message_id)


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
    # تشغيل سيرفر الويب في مسار خلفي
    t = Thread(target=run_web)
    t.start()
    # تشغيل البوت الأساسي
    start_bot()
