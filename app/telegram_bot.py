from telegram import Bot, ParseMode
import asyncio

class TelegramBot:
    def __init__(self, token=None, chat_id=None):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token) if token else None

    async def send_message(self, text):
        if not self.bot or not self.chat_id:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.bot.send_message, self.chat_id, text, ParseMode.HTML)

    async def send_signal(self, s: dict):
        txt = f"<b>Signal {s['side'].upper()}</b>\nSymbol: {s['symbol']}\nPrice: {s['price']:.5f}\nSL: {s['sl']:.5f}\nTP: {s['tp']:.5f}\nRSI: {s['rsi']:.2f}"
        await self.send_message(txt)
