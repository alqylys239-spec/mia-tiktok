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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # فك الرابط المختصر مع إضافة الـ headers لكي لا يرفضه تيك توك
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            try:
                r_short = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
                url = r_short.url.split('?')[0]
            except Exception as e:
                print(f"Error expanding URL: {e}")

        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, headers=headers, timeout=15)
        data_json = response.json()

        if data_json.get("code") == 0:
            video_data = data_json.get("data", {})
            video_url = video_data.get("play") or video_data.get("hdplay")
            
            if video_url:
                if video_url.startswith('/'):
                    video_url = f"https://www.tikwm.com{video_url}"
                    
                bot.send_video(message.chat.id, video_url, caption="✨ تم التحميل بنجاح بدون علامة مائية بواسطة البوت")
                bot.delete_message(message.chat.id, msg.message_id)
                return

        bot.edit_message_text("عذراً، تعذر جلب الفيديو. تأكد أن الرابط عام وليس خاصاً وجرب رابطاً آخر.", message.chat.id, msg.message_id)
        
    except Exception as e:
        print(f"Main Error: {e}")
        bot.edit_message_text(f"حدث خطأ تقني: {str(e)[:40]}", message.chat.id, msg.message_id)
