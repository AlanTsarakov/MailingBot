from dotenv import load_dotenv
import os
import telebot
import requests
import time


load_dotenv("keys.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
UNISENDER_API_KEY = os.getenv("UNISENDER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def add_to_unisender_list(email):
    base_url = "https://api.unisender.com/ru/api/subscribe"
    
    params = {
        "format": "json",
        "api_key": UNISENDER_API_KEY,
        "list_ids": "19843137",  
        "fields[email]": email,
        "fields[Name]": "Подписчик бота",  
        "tags": "telegram_bot,auto_subscribe",  
        "double_optin": "3", 
        "overwrite": "2"  
    }
    
    try:
        # Формируем URL с параметрами
        response = requests.get(base_url, params=params, timeout=10)  
        result = response.json()
        
        if 'result' in result and 'person_id' in result['result']:
            return {'success': True, 'person_id': result['result']['person_id']}
        else:
            return {'success': False, 'error': result.get('error', 'Unknown error')}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я бот для подписки на рассылку.\n\n"
        "Отправьте мне ваш email, и я добавлю вас в список рассылки.\n"
        "После этого вам придет письмо с PDF-документом."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=["text"])
def handle_email(message):
    email = message.text.strip()
    

    if "@" not in email or "." not in email or len(email) < 5:
        bot.reply_to(message, "❌ Пожалуйста, введите корректный email адрес.")
        return
    

    result = add_to_unisender_list(email)
    
    if result['success']:
        response_text = (
            "✅ Вы успешно подписаны!\n\n"
            f"Ваш ID в системе: {result['person_id']}\n"
            "Письмо с документами придет вам в течение нескольких минут."
        )
    else:
        error_msg = result.get('error', 'Неизвестная ошибка')
        response_text = (
            "❌ Произошла ошибка при подписке:\n"
            f"{error_msg}\n\n"
            "Попробуйте позже или свяжитесь с поддержкой."
        )
    
    bot.reply_to(message, response_text)


while True:
    try:
        print("🔄 Запуск бота...")
        bot.polling(none_stop=True, timeout=30)
    except Exception as e:
        print(f"⚠️ Ошибка: {e}. Перезапуск через 60 сек...")
        time.sleep(100)  # Ждём, пока Telegram починят
