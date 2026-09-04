from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from app.signal import SignalEngine
from app.telegram_bot import TelegramBot
import os

app = FastAPI(title="MT5 Gold Trader - MVP")

# Load config from env
SYMBOL = os.getenv("SYMBOL", "Gold")
TF = os.getenv("TIMEFRAME", "1h")

engine = SignalEngine(symbol=SYMBOL, timeframe=TF)
tg = TelegramBot(token=os.getenv("TELEGRAM_BOT_TOKEN"), chat_id=os.getenv("TELEGRAM_CHAT_ID"))

@app.on_event("startup")
async def startup_event():
    # start background polling
    app.add_task = None
    # simple background loop using FastAPI startup hooks could be added,
    # but to keep MVP simple, we rely on external scheduler or calling /check-signals
    pass

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ea/webhook")
async def ea_webhook(payload: Request):
    # EA or external source can POST tick/ohlc data here
    data = await payload.json()
    # expected: { "type": "tick" or "ohlc", "symbol": "...", "ohlc": {...} }
    engine.feed_external(data)
    return JSONResponse({"received": True})

@app.get("/check-signals")
async def check_signals(background: BackgroundTasks):
    signals = engine.generate_signals()
    # send notifications for new signals
    for s in signals:
        await tg.send_signal(s)
    return {"generated": len(signals), "signals": signals}
