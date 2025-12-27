import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import json
import os
import time
import threading

TOKEN = "7816401651:AAF9xWvCVLHDtTKitP28EKCnO8QFjlDIicw"
ADMIN_ID = 7348698420
CHANNEL_USERNAME = "@DAYS2GO"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ---------- USERS ----------
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump([], f)

def save_user(uid):
    with open("users.json", "r+") as f:
        users = json.load(f)
        if uid not in users:
            users.append(uid)
            f.seek(0)
            json.dump(users, f)

def total_users():
    with open("users.json") as f:
        return len(json.load(f))

# ---------- FORCE JOIN ----------
def is_joined(uid):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, uid).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

# ---------- UI ----------
def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📥 CAPCUT PRO", callback_data="capcut"),
        InlineKeyboardButton("📥 FILMORA PRO", callback_data="filmora"),
    )
    kb.add(
        InlineKeyboardButton("📥 KINEMASTER PRO", callback_data="kine"),
        InlineKeyboardButton("🏆 FF TOURNAMENT", callback_data="ff"),
    )
    return kb

def join_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
        InlineKeyboardButton("✅ Joined", callback_data="check")
    )
    return kb

# ---------- START ----------
@bot.message_handler(commands=["start"])
def start(m):
    save_user(m.from_user.id)

    if not is_joined(m.from_user.id):
        bot.send_message(
            m.chat.id,
            "❌ *Access Denied*\n\nJoin channel first 👇",
            parse_mode="Markdown",
            reply_markup=join_menu()
        )
        return

    bot.send_message(
        m.chat.id,
        "🔥 *WELCOME TO DAYS2GO BOT* 🔥\n\nChoose APK 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ---------- CALLBACKS ----------
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id

    if c.data == "check":
        if is_joined(uid):
            bot.edit_message_text(
                "✅ *Access Granted*\n\nSelect option 👇",
                c.message.chat.id,
                c.message.message_id,
                parse_mode="Markdown",
                reply_markup=main_menu()
            )
        else:
            bot.answer_callback_query(c.id, "Join channel first ❌", show_alert=True)

    links = {
        "capcut": "https://t.me/days2go/53",
        "filmora": "https://t.me/days2go/23",
        "kine": "https://t.me/days2go/46",
        "ff": "https://t.me/days2go/59"
    }

    if c.data in links:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("⬅️ Back", callback_data="back"))
        bot.edit_message_text(
            f"📥 *Download*\n\n👉 {links[c.data]}",
            c.message.chat.id,
            c.message.message_id,
            parse_mode="Markdown",
            reply_markup=kb
        )

    if c.data == "back":
        bot.edit_message_text(
            "🏠 *Main Menu*",
            c.message.chat.id,
            c.message.message_id,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

# ---------- ADMIN ----------
@bot.message_handler(commands=["admin"])
def admin(m):
    if m.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        m.chat.id,
        f"👑 ADMIN PANEL\n\n👥 Users: {total_users()}"
    )

# ---------- WEBHOOK ----------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "OK"

@app.route("/")
def index():
    return "Bot is running"

def set_webhook():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://YOUR-RENDER-URL/{TOKEN}")

if __name__ == "__main__":
    threading.Thread(target=set_webhook).start()
    app.run(host="0.0.0.0", port=10000)