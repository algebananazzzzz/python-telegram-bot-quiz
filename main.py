import os
import handlers
from mypersistence import MyPersistence
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PollAnswerHandler,
    filters,
    PersistenceInput,
)

passphrase = os.environ.get('PASSPHRASE')


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    persistence = MyPersistence(redis_key=os.environ.get('REDIS_KEY'), store_data=PersistenceInput(
        bot_data=False, chat_data=False), update_interval=60)
    application = Application.builder().token(
        os.environ.get('TOKEN')).persistence(persistence).build()

    application.add_handler(CommandHandler("start", handlers.start))

    if passphrase:
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, handlers.select_quiz))
        application.add_handler(MessageHandler(
            filters.COMMAND, handlers.help_handler))
    else:
        application.add_handler(CommandHandler("quiz", handlers.select_quiz))
        application.add_handler(MessageHandler(
            filters.TEXT, handlers.help_handler))

    application.add_handler(CallbackQueryHandler(
        handlers.quiz, pattern="^\d+$"))
    application.add_handler(PollAnswerHandler(handlers.receive_poll_answer))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
