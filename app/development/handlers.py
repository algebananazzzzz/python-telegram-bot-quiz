import os
import json
from telegram.constants import ParseMode
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes


with open('data.json') as f:
    data = json.load(f)

passphrase = os.environ.get('PASSPHRASE')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    start_msg = os.environ.get('START_MESSAGE')
    if not start_msg:
        start_msg = str()
    if passphrase:
        start_msg += " Please provide the passphrase to continue."
    else:
        start_msg += " /quiz to continue."
    start_message = await update.message.reply_text(start_msg)

    await context.bot.pin_chat_message(chat_id=update.effective_chat.id, message_id=start_message.message_id)


async def select_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if passphrase:
        if update.message.text != passphrase:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong passphrase.")
            return

    keyboard = list()
    for index, quiz in enumerate(data):
        keyboard.append([
            InlineKeyboardButton(
                quiz['quiz_name'], callback_data=str(index))])

    markup = InlineKeyboardMarkup(
        keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please select which quiz to take", reply_markup=markup)


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a predefined poll"""
    query = update.callback_query
    user_data = context.user_data
    if query:
        quiz_number = int(query.data)
        await query.answer()
        await query.delete_message()
        number = 0
        score = 0
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, "You are taking quiz: {}. There are {} questions.".format(data[quiz_number]['quiz_name'], len(data[quiz_number]['quiz_data'].items())))
    else:
        number = user_data['number']
        quiz_number = user_data['quiz_number']
        chat_id = user_data["chat_id"]
        score = user_data["score"]

    try:
        question, poll_data = list(
            data[quiz_number]['quiz_data'].items())[number]
    except IndexError:
        user_data.clear()
        if passphrase:
            await context.bot.send_message(chat_id, "Congrats! You have reached the end of the quiz. Your score is {} out of {} questions. Provide passphrase again to take again / another quiz.".format(score, len(data[quiz_number]['quiz_data'].items())))
        else:
            await context.bot.send_message(chat_id, "Congrats! You have reached the end of the quiz. Your score is {} out of {} questions. /quiz to take again / another quiz".format(score, len(data[quiz_number]['quiz_data'].items())))
        return

    if len(question) > 300:
        await context.bot.send_message(
            chat_id, text=question, parse_mode=ParseMode.HTML)
        question = "Options:"

    options = poll_data['options']
    option_msg = str()
    for i, o in enumerate(options):
        if len(o) > 100:
            option_msg += ("<b>Option {}:</b> {}\n".format(i + 1, o))
            options[i] = "Refer to Option {} below".format(i + 1)
    answer = poll_data['answer']
    message = await context.bot.send_poll(
        chat_id=chat_id,
        type='quiz',
        question=question,
        correct_option_id=answer,
        options=options,
        is_anonymous=False,
    )
    if option_msg != str():
        await context.bot.send_message(chat_id, option_msg, parse_mode=ParseMode.HTML)
    # Save some info about the poll the user_data for later use in receive_poll_answer
    if query:
        payload = {
            message.poll.id: answer,
            'score': score,
            'chat_id': chat_id,
            'number': number,
            'quiz_number': quiz_number
        }
    else:
        payload = {
            message.poll.id: answer
        }

    user_data.update(payload)


async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Summarize a users poll vote"""
    poll_answer = update.poll_answer
    user_data = context.user_data
    try:
        answer = user_data[poll_answer.poll_id]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return

    score = user_data['score']
    chat_id = user_data['chat_id']
    # await context.bot.stop_poll(answered_poll_data["chat_id"], answered_poll_data["message_id"])
    if poll_answer.option_ids[0] == answer:
        score += 1
        # await context.bot.send_message(answered_poll_data["chat_id"], "Correct answer. Good job!")
    else:
        await context.bot.send_message(chat_id, "Wrong answer. Your current score is {}.".format(score))

    payload = {
        "quiz_number": user_data['quiz_number'],
        "score": score,
        "number": user_data['number'] + 1,
        "chat_id": chat_id
    }
    user_data.clear()
    user_data.update(payload)
    return await quiz(update, context)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    if passphrase:
        await update.message.reply_text("You have to produce passphrase first before accessing quiz!")
    else:
        await update.message.reply_text("/quiz to access quiz")
