import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PollAnswerHandler,
    filters,
)
from handlers import (
    start,
    select_quiz,
    quiz,
    receive_poll_answer,
    help_handler,
)

passphrase = os.environ.get('PASSPHRASE')


application = Application.builder().token(
    os.environ.get('TOKEN')).build()

application.add_handler(CommandHandler("start", start))

if passphrase:
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, select_quiz))
    application.add_handler(MessageHandler(filters.COMMAND, help_handler))
else:
    application.add_handler(CommandHandler("quiz", select_quiz))
    application.add_handler(MessageHandler(filters.TEXT, help_handler))

application.add_handler(CallbackQueryHandler(quiz, pattern="^\d+$"))
application.add_handler(PollAnswerHandler(receive_poll_answer))


def main():
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
