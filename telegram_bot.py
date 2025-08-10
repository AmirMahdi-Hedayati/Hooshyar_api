import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Read tokens from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text("سلام! من ربات هوشیار هستم. سوال خود را بپرسید تا پاسخ بدهم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages by forwarding them to the OpenAI API and sending back the answer."""
    user_message = update.message.text

    if not OPENAI_API_KEY:
        await update.message.reply_text("کلید API برای سرویس GPT تنظیم نشده است.")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        answer = response.choices[0].message["content"].strip()
        await update.message.reply_text(answer)
    except Exception as e:
        logging.exception("Error communicating with OpenAI API")
        await update.message.reply_text("متأسفانه خطایی رخ داد. لطفاً بعداً دوباره امتحان کنید.")


def main() -> None:
    """Start the Telegram bot."""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
