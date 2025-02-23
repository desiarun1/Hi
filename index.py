import telebot
import random
import pymongo
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "7891840653:AAHJzAP8xFeu33R3KK1Eyx6dt2fN8quMCQE"
MONGO_URI = "YOUR_MONGODB_URI"
ADMIN_ID = YOUR_TELEGRAM_USER_ID  # Replace with your Telegram user ID
WEB_APP_URL = "https://your-web-app-url.com"  # Replace with your hosted web app URL

bot = telebot.TeleBot(TOKEN)
client = pymongo.MongoClient(MONGO_URI)
db = client["telegram_bot"]
users = db["users"]

SPIN_REWARDS = [5, 10, 15, 20, 50, 0]  # Possible spin rewards

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    ref_code = message.text.split(" ")[1] if len(message.text.split()) > 1 else None
    
    user = users.find_one({"user_id": user_id})
    if not user:
        users.insert_one({"user_id": user_id, "balance": 0, "referrals": 0, "last_bonus": None, "spins": 0})
        if ref_code and ref_code.isdigit():
            referrer_id = int(ref_code)
            referrer = users.find_one({"user_id": referrer_id})
            if referrer:
                users.update_one({"user_id": referrer_id}, {"$inc": {"balance": 10, "referrals": 1, "spins": 1}})
                bot.send_message(referrer_id, "🎉 आपने एक नया रेफरल कमाया! ₹10 और 1 स्पिन आपके अकाउंट में जुड़ गए हैं।")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎡 Spin & Earn", web_app=WebAppInfo(url=WEB_APP_URL)))
    markup.add(InlineKeyboardButton("💰 Check Balance", callback_data="balance"))
    markup.add(InlineKeyboardButton("🎁 Daily Bonus", callback_data="dailybonus"))
    markup.add(InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"))
    bot.send_message(message.chat.id, "👋 Welcome! Choose an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user = users.find_one({"user_id": call.message.chat.id})
    if call.data == "balance":
        bot.answer_callback_query(call.id, f"💰 Your Balance: ₹{user['balance']} | 🎡 Spins Left: {user['spins']}")
    elif call.data == "dailybonus":
        today = datetime.now().date()
        if user['last_bonus'] == str(today):
            bot.answer_callback_query(call.id, "🔄 आपने आज का बोनस पहले ही ले लिया है।")
        else:
            bonus = random.randint(5, 20)
            users.update_one({"user_id": call.message.chat.id}, {"$inc": {"balance": bonus}, "$set": {"last_bonus": str(today)}})
            bot.answer_callback_query(call.id, f"🎁 आपने ₹{bonus} का डेली बोनस प्राप्त किया!")
    elif call.data == "withdraw":
        bot.send_message(ADMIN_ID, f"🔔 Withdrawal request from {call.message.chat.id} for ₹{user['balance']}.")
        bot.send_message(call.message.chat.id, "✅ Withdrawal request sent to admin. Please wait for approval.")

bot.polling()
