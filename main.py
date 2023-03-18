import datetime
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

load_dotenv()
BOT_TOKEN = os.environ.get('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def time(update, context):
    await update.message.reply_text(f'Текущее время: {datetime.datetime.now().time()}')


async def date(update, context):
    await update.message.reply_text(f'Сегодня: {datetime.datetime.now().date()}')


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляем задачу в очередь"""
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    try:
        t = int(context.args[0])
    except TypeError as err:
        logger.error(err)
        await update.effective_message.reply_text('Параметр должен быть целым число')
        return
    except IndexError as err:
        logger.error(err)
        await update.effective_message.reply_text('Нужно указать параметр')
        return
    context.job_queue.run_once(task, t, chat_id=chat_id, name=str(chat_id), data=t)

    text = f'Вернусь через {t} с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def task(context):
    """Выводит сообщение"""
    t = context.job.data
    await context.bot.send_message(context.job.chat_id, text=f'КУКУ! {t}c. прошли!')


async def unset(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('set_timer', set_timer))
    application.add_handler(CommandHandler('unset', unset))
    application.run_polling()


if __name__ == '__main__':
    main()
