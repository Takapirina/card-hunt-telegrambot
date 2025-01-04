import asyncio
from telegram import Update
from telegram.ext import CallbackContext

async def send_sticker_example(update: Update, context: CallbackContext):
    sticker_id = "CAACAgIAAxkBAAENZ-dncG3d01MicXCk8oKW2D7aILl4UAACSgMAArVx2gbCfgb6m0gexDYE"
    
    sent_message = await context.bot.send_sticker(
        chat_id=update.effective_chat.id,
        sticker=sticker_id
    )

    await asyncio.sleep(3)

    await context.bot.delete_message(
        chat_id=sent_message.chat_id,
        message_id=sent_message.message_id
    )