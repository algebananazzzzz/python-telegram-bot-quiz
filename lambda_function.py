import os
import json
import asyncio
import handlers
from mypersistence import MyPersistence
from telegram import Update
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

persistence = MyPersistence(redis_key=os.environ.get("REDIS_KEY"), store_data=PersistenceInput(
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

application.add_handler(CallbackQueryHandler(handlers.quiz, pattern="^\d+$"))
application.add_handler(PollAnswerHandler(handlers.receive_poll_answer))


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(main(event, context))


async def main(event, context):
    try:
        await application.initialize()
        await application.process_update(Update.de_json(json.loads(event["body"]), application.bot))
        await application.update_persistence()
        await persistence.flush()
        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': 'Failure'
        }
