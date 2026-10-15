@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def handle_tiktok(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        bot.send_message(message.chat.id, "عذراً، يجب عليك الاشتراك في القناة والقروب أولاً لتتمكن من التحميل!")
        return

    msg = bot.send_message(message.chat.id, "جاري تحميل الفيديو بدون علامة مائية... ⏳")
    
    try:
        url = message.text.strip()
        
        # إذا كان الرابط مختصراً، نقوم بفك الرابط أولاً لنحصل على الرابط الحقيقي
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            try:
                r_short = requests.get(url, allow_redirects=True, timeout=10)
                url = r_short.url.split('?')[0] # تنظيف الرابط من الزوائد
            except:
                pass

        # استخدام API بديل ومضمون لتنزيل التيك توك بدون علامة مائية
        api_url = f"https://tikwm.com/api/?url={url}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(api_url, headers=headers)
        data_json = response.json()

        if data_json.get("code") == 0:
            video_data = data_json.get("data", {})
            video_url = video_data.get("play")
            
            if video_url:
                if video_url.startswith('/'):
                    video_url = f"https://www.tikwm.com{video_url}"
                    
                bot.send_video(message.chat.id, video_url, caption="✨ تم التحميل بنجاح بدون علامة مائية بواسطة البوت")
                bot.delete_message(message.chat.id, msg.message_id)
                return

        bot.edit_message_text("عذراً، تعذر جلب الفيديو. تأكد أن الرابط عام وليس خاصاً.", message.chat.id, msg.message_id)
        
    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("حدث خطأ تقني أثناء التحميل، حاول مجدداً.", message.chat.id, msg.message_id)
