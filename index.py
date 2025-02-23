import telebot
import random
from datetime import datetime, timedelta

TOKEN = "7891840653:AAHJzAP8xFeu33R3KK1Eyx6dt2fN8quMCQE"
bot = telebot.TeleBot(TOKEN)

users = {}  # Simple user data store (Use Database in Production)
tasks = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    ref_code = message.text.split(" ")[1] if len(message.text.split()) > 1 else None
    
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "last_bonus": None}
        if ref_code and ref_code.isdigit():
            referrer_id = int(ref_code)
            if referrer_id in users:
                users[referrer_id]["balance"] += 10  # ₹10 for referral
                users[referrer_id]["referrals"] += 1
                bot.send_message(referrer_id, "🎉 आपने एक नया रेफरल कमाया! ₹10 आपके अकाउंट में जुड़ गए हैं।")
    
    bot.reply_to(message, f"👋 Welcome! Use /balance to check balance.\nRefer & Earn: ₹10 per referral!\nYour Referral Link: t.me/YourBot?start={user_id}")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    user_id = message.chat.id
    if user_id in users:
        balance = users[user_id]["balance"]
        bot.reply_to(message, f"💰 Your Balance: ₹{balance}\nUse /withdraw to redeem.")
    else:
        bot.reply_to(message, "🔴 पहले /start दबाएं।")

@bot.message_handler(commands=['dailybonus'])
def daily_bonus(message):
    user_id = message.chat.id
    today = datetime.now().date()
    
    if users[user_id]["last_bonus"] == today:
        bot.reply_to(message, "🔄 आपने आज का बोनस पहले ही ले लिया है।")
    else:
        bonus = random.randint(5, 20)  # ₹5-₹20 Random Bonus
        users[user_id]["balance"] += bonus
        users[user_id]["last_bonus"] = today
        bot.reply_to(message, f"🎁 आपने ₹{bonus} का डेली बोनस प्राप्त किया! /balance देखें।")

@bot.message_handler(commands=['withdraw'])
def withdraw_funds(message):
    user_id = message.chat.id
    balance = users[user_id]["balance"]
    
    if balance < 50:
        bot.reply_to(message, "❌ न्यूनतम निकासी ₹50 है।")
        return
    
    bot.reply_to(message, "🔹 कृपया अपना UPI ID भेजें (जैसे example@upi)")
    bot.register_next_step_handler(message, process_upi, user_id)

def process_upi(message, user_id):
    upi_id = message.text
    if "@" in upi_id:
        bot.reply_to(message, f"✅ ₹{users[user_id]['balance']} आपके UPI ({upi_id}) पर भेज दिए जाएंगे।")
        users[user_id]["balance"] = 0
        # यहाँ Razorpay या Cashfree API से ऑटो-पेमेंट जोड़ें।
    else:
        bot.reply_to(message, "❌ गलत UPI ID! फिर से /withdraw आज़माएं।")

bot.polling()
