from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import asyncio
import json

TOKEN = os.getenv("TOKEN")
OWNER_ID = 523087272

DATA_FILE = "data.json"

# Load data
try:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
except:
    data = {"notes": [], "users": []}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def is_owner(user_id):
    return user_id == OWNER_ID

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in data["users"]:
        data["users"].append(user.id)
        save_data()

    if is_owner(user.id):
        await update.message.reply_text("👑 PRO BOT READY")
    else:
        await update.message.reply_text("📩 Send message. Admin or AI will reply.")

# Save note
async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    text = " ".join(context.args)
    data["notes"].append(text)
    save_data()

    await update.message.reply_text("Saved ✅")

# Show notes
async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    await update.message.reply_text("\n".join(data["notes"]) or "No notes")

# Reminder
async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    seconds = int(context.args[0])
    msg = " ".join(context.args[1:])

    await update.message.reply_text(f"⏰ Reminder set")

    await asyncio.sleep(seconds)
    await update.message.reply_text(f"🔔 {msg}")

# Show users
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    await update.message.reply_text("\n".join(map(str, data["users"])) or "No users")

# Reply to user
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    try:
        user_id = int(context.args[0])
        msg = " ".join(context.args[1:])
    except:
        await update.message.reply_text("Use: /reply user_id message")
        return

    await context.bot.send_message(chat_id=user_id, text=f"💬 {msg}")

# Forward text messages
async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_owner(user.id):
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"📩 ID:{user.id}\n{user.first_name}: {update.message.text}"
        )

        # SIMPLE AI REPLY (auto)
        await update.message.reply_text("🤖 I received your message!")

# Handle photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_owner(user.id):
        photo = update.message.photo[-1].file_id

        await context.bot.send_photo(
            chat_id=OWNER_ID,
            photo=photo,
            caption=f"📸 From {user.first_name} (ID:{user.id})"
        )

# Handle documents
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_owner(user.id):
        doc = update.message.document.file_id

        await context.bot.send_document(
            chat_id=OWNER_ID,
            document=doc,
            caption=f"📁 From {user.first_name} (ID:{user.id})"
        )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("save", save))
app.add_handler(CommandHandler("notes", notes))
app.add_handler(CommandHandler("remind", remind))
app.add_handler(CommandHandler("users", users))
app.add_handler(CommandHandler("reply", reply))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

app.run_polling()
