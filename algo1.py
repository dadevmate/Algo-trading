# NORMAL OLLAMA CALL:
'''
from ollama import chat

# Send a chat-style prompt to the pulled model
response = chat(
  model='llama3.2:1b',
  messages=[{'role': 'user', 'content': 'What is the capital of France?'}]
)

print(response.message.content)

'''
# COMPLETION TYPE OLLAMA CALL:
'''

from ollama import generate

result = generate('llama3.2:1b', 'Translate to French: "Good morning"')
print(result['response'])

'''

import ibapi, ib_insync, alpaca_trade_api
import yfinance as yf
import ollama

print("IB API:", ibapi.__version__)
print("ib_insync:", ib_insync.__version__)
print("Alpaca API:", alpaca_trade_api.__version__)


# pip install alpaca-trade-api
from alpaca_trade_api.rest import REST, TimeFrame, APIError

# 1) Configuration: replace with your actual keys or load from env vars/config file
API_KEY = "PK3610I5ATPMJZF046XX"
API_SECRET = "1aLNghxvbEpB95n9hnECuqOofJDDdrczcfGGKdX3"
BASE_URL = "https://paper-api.alpaca.markets"  # use paper trading endpoint

# 2) Initialize REST client
api = REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# 3) Check account status
account = api.get_account()
print(f"Account status: {account.status}, Buying power: {account.buying_power}")

# 4) Submit a market buy order
try:
    buy_order = api.submit_order(
        symbol="AAPL",        # ticker you want to trade
        qty=1,                # number of shares
        side="buy",           # "buy" or "sell"
        type="market",        # "market", "limit", "stop", etc.
        time_in_force="day"   # "day", "gtc", "ioc", "fok"
    )
    print("Buy order submitted:", buy_order)
except APIError as e:
    print("Error placing buy order:", e)

# 5) Submit a market sell order
try:
    sell_order = api.submit_order(
        symbol="AAPL",
        qty=1,
        side="sell",
        type="market",
        time_in_force="day"
    )
    print("Sell order submitted:", sell_order)
except APIError as e:
    print("Error placing sell order:", e)

# 6) Check existing positions
positions = api.list_positions()
for pos in positions:
    print(f"{pos.symbol}: {pos.qty} shares @ avg ${pos.avg_entry_price}")

# 7) Cancel an order by ID (if needed)
# api.cancel_order(buy_order.id)
