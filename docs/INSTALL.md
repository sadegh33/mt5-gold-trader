# راهنمای سریع نصب MVP

1) ساخت ربات تلگرام
- در Telegram به BotFather پیام دهید و یک bot بسازید، توکن را کپی کنید.
- Chat ID را با یکی از روش‌ها (مثلاً ارسال پیام به bot و استفاده از https://api.telegram.org/bot<token>/getUpdates) بدست آورید.

2) مقداردهی .env
- فایل .env.example را کپی کنید به .env و مقادیر TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID و SERVER_PUBLIC_URL را قرار دهید.

3) اجرای محلی
- pip install -r requirements.txt
- uvicorn app.main:app --host 0.0.0.0 --port 8000

4) اجرای با Docker
- docker build -t mt5-gold-bot .
- docker run --env-file .env -p 8000:8000 mt5-gold-bot

5) اتصال EA (برای اجرای خودکار)
- EA_MT5_Gold.mq5 را در MetaEditor باز کنید و سرور (ServerURL) را مقداردهی کنید.
- آدرس را در Tools->Options->Expert Advisors->Allow WebRequest for listed URL اضافه کنید.
- EA را در چارت نماد Gold در MT5 اجرا کنید تا tickها به سرور ارسال شوند.

6) تست سیگنال
- بعد از بالا آمدن سرور، endpoint /check-signals را فراخوانی کنید تا سیگنال‌ها محاسبه و در تلگرام ارسال شوند.
