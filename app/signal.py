import pandas as pd
import numpy as np
import yfinance as yf
import os
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from datetime import datetime, timedelta

class SignalEngine:
    def __init__(self, symbol="Gold", timeframe="1h"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.ema_short = int(os.getenv("EMA_SHORT", 20))
        self.ema_long = int(os.getenv("EMA_LONG", 50))
        self.rsi_period = int(os.getenv("RSI_PERIOD", 14))
        self.atr_period = int(os.getenv("ATR_PERIOD", 14))
        self.max_per_day = int(os.getenv("MAX_TRADES_PER_DAY", 3))
        self.history = None
        self.last_signals = []

    def fetch_ohlc(self, period="7d"):
        # MVP: use yfinance symbol mapping for Gold: 'XAUUSD=X'
        yf_symbol = "XAUUSD=X"
        df = yf.download(yf_symbol, period=period, interval=self._yf_interval())
        if df.empty:
            return None
        df = df.dropna()
        return df

    def _yf_interval(self):
        # map timeframe to yfinance interval
        if self.timeframe == "1h":
            return "60m"
        if self.timeframe == "15m":
            return "15m"
        return "1h"

    def compute_indicators(self, df: pd.DataFrame):
        df["ema_short"] = EMAIndicator(df["Close"], window=self.ema_short).ema_indicator()
        df["ema_long"] = EMAIndicator(df["Close"], window=self.ema_long).ema_indicator()
        df["rsi"] = RSIIndicator(df["Close"], window=self.rsi_period).rsi()
        df["atr"] = AverageTrueRange(df["High"], df["Low"], df["Close"], window=self.atr_period).average_true_range()
        return df

    def generate_signals(self):
        df = self.fetch_ohlc()
        if df is None:
            return []
        df = self.compute_indicators(df)
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else None
        signals = []

        # EMA cross
        if prev is not None:
            cross_up = (prev["ema_short"] <= prev["ema_long"]) and (last["ema_short"] > last["ema_long"])
            cross_down = (prev["ema_short"] >= prev["ema_long"]) and (last["ema_short"] < last["ema_long"]) 
        else:
            cross_up = cross_down = False

        # RSI filter
        rsi = last["rsi"]
        if cross_up and rsi > 30 and rsi < 70:
            s = self._build_signal("buy", last)
            if not self._is_duplicate(s):
                signals.append(s)
        if cross_down and rsi > 30 and rsi < 70:
            s = self._build_signal("sell", last)
            if not self._is_duplicate(s):
                signals.append(s)

        # store signals briefly
        for s in signals:
            self.last_signals.append({"time": datetime.utcnow(), "signal": s})
        # prune older than 24h
        self.last_signals = [x for x in self.last_signals if x["time"] > datetime.utcnow() - timedelta(hours=24)]
        return signals

    def _build_signal(self, side, last_row):
        atr = last_row["atr"] if not np.isnan(last_row["atr"]) else 0
        sl = last_row["Close"] - atr * 1.5 if side == "buy" else last_row["Close"] + atr * 1.5
        rr = 2.0
        tp = last_row["Close"] + (last_row["Close"] - sl) * rr if side == "buy" else last_row["Close"] - (sl - last_row["Close"]) * rr
        return {
            "symbol": self.symbol,
            "side": side,
            "price": float(last_row["Close"]),
            "sl": float(sl),
            "tp": float(tp),
            "rsi": float(last_row["rsi"]),
            "atr": float(atr),
            "time": str(last_row.name)
        }

    def _is_duplicate(self, signal):
        # simple dedupe: same side and price within small tolerance in last 60 minutes
        for s in self.last_signals:
            if s["signal"]["side"] == signal["side"] and abs(s["signal"]["price"] - signal["price"]) < 1e-6:
                return True
        return False

    def feed_external(self, data):
        # EA can push data here in future — for now we just accept and ignore
        pass
