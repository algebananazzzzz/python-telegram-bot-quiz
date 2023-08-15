import os
import json
import redis
import asyncio
from mypersistence import MyPersistence
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

redis_endpoint = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]
redis_key = os.environ["REDIS_KEY"]

try:
    redis_conn = redis.StrictRedis(host=redis_endpoint, port=redis_port)
except Exception:
    redis_conn = None

persistence = MyPersistence(redis_conn=redis_conn,
                            redis_key=os.environ.get("REDIS_KEY"))

application = Application.builder().token(
    os.environ.get('TOKEN')).persistence(persistence).build()

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


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(main(event, context))


async def main(event, context):
    request = Update.de_json(json.loads(event["body"]), application.bot)

    try:
        await persistence.load_active_user(request.effective_user.id)
        await application.initialize()
        await application.process_update(request)
        await application.update_persistence()
        await persistence.flush()

        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': 'Failure'
        }
