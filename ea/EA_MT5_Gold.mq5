//+------------------------------------------------------------------+
//| EA skeleton: sends basic order info / tick to server via HTTP    |
//| NOTE: This is a minimal starting point. You must adapt for your  |
//| broker symbol naming (e.g., "Gold") and add error handling.      |
//+------------------------------------------------------------------+
#property copyright "MT5 Gold EA"
#property version   "1.00"

input string ServerURL = "https://your-server.example.com/ea/webhook";
input string SymbolName = "Gold";
input int    IntervalSeconds = 60;

int OnInit()
  {
   EventSetTimer(IntervalSeconds);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
  }

void OnTimer()
  {
   // collect last tick
   MqlTick tick;
   if(SymbolInfoTick(SymbolName,tick))
     {
      string body = "{";
      body += "\"type\":\"tick\",";
      body += "\"symbol\":\""+SymbolName+"\",";
      body += "\"bid\":"+DoubleToString(tick.bid, _Digits)+",";
      body += "\"ask\":"+DoubleToString(tick.ask, _Digits)+",";
      body += "\"time\":"+IntegerToString((int)TimeCurrent());
      body += "}";
      // send HTTP POST (using WebRequest)
      string headers="Content-Type: application/json\r\n";
      char result[];
      int res = WebRequest("POST", ServerURL, headers, 0, body, result, NULL, NULL);
      // NOTE: You must add ServerURL to Tools->Options->Expert Advisors->Allow WebRequest for listed URL
     }
  }
