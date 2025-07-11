
## FOR LIVE PAPER TRADING

import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone

# ─── 1. CONFIGURE YOUR KEYS ────────────────────────────────────────────────────
API_KEY    = "PK3610I5ATPMJZF046XX"
API_SECRET = "1aLNghxvbEpB95n9hnECuqOofJDDdrczcfGGKdX3"
BASE_URL   = "https://paper-api.alpaca.markets"
SYMBOL     = "AAPL"

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# ─── 2. RSI CALCULATION ────────────────────────────────────────────────────────
def compute_rsi(series, period=14):
    delta     = series.diff()
    gain      = delta.clip(lower=0)
    loss      = -delta.clip(upper=0)
    avg_gain  = gain.rolling(period).mean()
    avg_loss  = loss.rolling(period).mean()
    rs        = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ─── 3. FETCH HISTORICAL BARS ─────────────────────────────────────────────────
def fetch_daily_bars(symbol, limit=500):
    bars = api.get_bars(
        symbol,
        tradeapi.TimeFrame.Day,
        limit=limit,
        adjustment='raw',
        feed='iex'
    ).df
    bars.index = pd.to_datetime(bars.index).tz_convert(None)
    return bars

# ─── 4. DETERMINE SIGNAL ───────────────────────────────────────────────────────
def latest_signal(df, rsi_period=14, entry_thresh=30, exit_thresh=50):
    # require enough bars
    if df is None or len(df) < rsi_period + 1:
        print(f"{datetime.now()}: Not enough data to compute RSI (bars={len(df) if df is not None else 0})")
        return None, None

    df = df.copy()
    df['rsi'] = compute_rsi(df['close'], period=rsi_period)
    df.dropna(inplace=True)
    if df.empty:
        print(f"{datetime.now()}: RSI computation resulted in empty DataFrame")
        return None, None

    last_rsi = df['rsi'].iloc[-1]
    if last_rsi < entry_thresh:
        return 1, last_rsi
    elif last_rsi > exit_thresh:
        return 0, last_rsi
    # hold previous
    prev_rsi = df['rsi'].iloc[-2]
    return (1 if prev_rsi < entry_thresh else 0), last_rsi

# ─── 5. EXECUTE ORDER ─────────────────────────────────────────────────────────
def execute_trade(desired_signal):
    try:
        pos = api.get_position(SYMBOL)
        current_qty = int(pos.qty)
    except tradeapi.rest.APIError:
        current_qty = 0

    if desired_signal == 1 and current_qty == 0:
        cash = float(api.get_account().cash)
        price = float(api.get_last_trade(SYMBOL).price)
        qty = int(cash // price)
        if qty > 0:
            api.submit_order(symbol=SYMBOL, qty=qty, side='buy', type='market', time_in_force='day')
            print(f"{datetime.now()}: BUY {qty} shares @ ~{price}")
    elif desired_signal == 0 and current_qty > 0:
        api.submit_order(symbol=SYMBOL, qty=current_qty, side='sell', type='market', time_in_force='day')
        print(f"{datetime.now()}: SELL {current_qty} shares")
    else:
        print(f"{datetime.now()}: No trade needed (signal={desired_signal}, position={current_qty})")

# ─── 6. MAIN LOOP ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    while True:
        now = datetime.now(timezone.utc)
        if now.weekday() < 5 and now.hour in range(13, 21):  # ET 9:30-16:00
            bars = fetch_daily_bars(SYMBOL)
            signal, rsi = latest_signal(bars)
            if signal is not None:
                print(f"{datetime.now()}: RSI={rsi:.2f}, signal={signal}")
                execute_trade(signal)
            else:
                print(f"{datetime.now()}: No valid signal; skipping trade execution.")
            time.sleep(60 * 60)
        else:
            print(f"{datetime.now()}: Market closed — skipping trading logic.")
            time.sleep(60 * 30)


'''
## FOR BACKTESTING normal strategy

import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

pd.set_option('future.no_silent_downcasting', True)

# ─── 1. CONFIGURE KEYS & PORTFOLIO ─────────────────────────────────────────────
API_KEY    = "PK3610I5ATPMJZF046XX"
API_SECRET = "1aLNghxvbEpB95n9hnECuqOofJDDdrczcfGGKdX3"
BASE_URL   = "https://paper-api.alpaca.markets"
ASSET_SYMBOLS = ["AAPL", "MSFT", "GOOG", "TLT", "GLD"]  # multi-asset symbols
MARKET_SYMBOL = "SPY"  # market proxy for CAPM
ROLL_WINDOW = 60      # days for CAPM rolling regression
MA_WINDOW   = 200     # days for trend filter
RF_ANN      = 0.02    # annual risk-free rate
RF_DAILY    = RF_ANN / 252
INITIAL_CAP = 100_000

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# ─── 2. FETCH DAILY CLOSES FOR ALL SYMBOLS INCLUDING MARKET ────────────────────
def fetch_closes(symbols, start, end):
    all_closes = {}
    for sym in symbols:
        bars = api.get_bars(
            sym,
            tradeapi.TimeFrame.Day,
            start=start.strftime('%Y-%m-%d'),
            end=(end + timedelta(days=1)).strftime('%Y-%m-%d'),
            adjustment='raw',
            feed='iex'
        ).df
        if isinstance(bars.index, pd.MultiIndex):
            bars = bars.xs(sym, level=1)
        closes = bars['close'].rename(sym)
        closes.index = pd.to_datetime(closes.index)
        all_closes[sym] = closes
    return pd.DataFrame(all_closes)

# ─── 3. COMPUTE SIGNALS PER ASSET ───────────────────────────────────────────────
def compute_signals(df_prices):
    signals = pd.DataFrame(index=df_prices.index, columns=ASSET_SYMBOLS)
    alphas  = pd.DataFrame(index=df_prices.index, columns=ASSET_SYMBOLS)
    market = df_prices[MARKET_SYMBOL]

    for sym in ASSET_SYMBOLS:
        asset = df_prices[sym]
        data = pd.concat([asset, market], axis=1).dropna()
        data.columns = [sym, MARKET_SYMBOL]
        # compute returns
        data['r_a'] = data[sym].pct_change()
        data['r_m'] = data[MARKET_SYMBOL].pct_change()
        data = data.dropna()
        # excess returns
        data['e_a'] = data['r_a'] - RF_DAILY
        data['e_m'] = data['r_m'] - RF_DAILY
        # rolling CAPM alpha
        alpha_list = []
        for i in range(len(data)):
            if i < ROLL_WINDOW:
                alpha_list.append(np.nan)
                continue
            window = data.iloc[i-ROLL_WINDOW:i]
            X = np.vstack([np.ones(len(window)), window['e_m']]).T
            y = window['e_a'].values
            coef = np.linalg.inv(X.T @ X) @ (X.T @ y)
            alpha_list.append(coef[0])
        data['alpha'] = alpha_list
        # trend filter
        data['ma'] = data[sym].rolling(MA_WINDOW).mean()
        # signal generation: 1 if alpha>0 and above MA
        sig = ((data['alpha'] > 0) & (data[sym] > data['ma'])).astype(int)
        signals.loc[data.index, sym] = sig
        alphas.loc[data.index, sym]  = data['alpha']

    # forward fill and fill zeros
    signals = signals.ffill().fillna(0).astype(int)
    return signals, alphas

# ─── 4. BACKTEST MULTI-ASSET PORTFOLIO ──────────────────────────────────────────
def backtest_portfolio(prices, signals):
    dates = prices.index
    cash = INITIAL_CAP
    holdings = pd.Series(0, index=ASSET_SYMBOLS)
    portfolio = []

    for date in dates:
        sigs = signals.loc[date]
        weights = sigs / sigs.sum() if sigs.sum() > 0 else pd.Series(0, index=ASSET_SYMBOLS)

        total_val = cash + (holdings * prices.loc[date, ASSET_SYMBOLS]).sum()
        target_dollars = weights * total_val
        new_shares = (target_dollars // prices.loc[date, ASSET_SYMBOLS]).astype(int)
        cash = total_val - (new_shares * prices.loc[date, ASSET_SYMBOLS]).sum()
        holdings = new_shares

        portfolio.append({'date': date, 'total': total_val})

    df = pd.DataFrame(portfolio).set_index('date')
    df['returns'] = df['total'].pct_change().fillna(0)
    return df

# ─── 5. METRICS ─────────────────────────────────────────────────────────────────
def compute_metrics(portfolio_df):
    # Annualized Return (CAGR)
    start_val = portfolio_df['total'].iloc[0]
    end_val = portfolio_df['total'].iloc[-1]
    days = (portfolio_df.index[-1] - portfolio_df.index[0]).days
    cagr = (end_val / start_val) ** (365.0 / days) - 1

    # Volatility (annualized)
    vol = portfolio_df['returns'].std() * np.sqrt(252)

    # Sharpe Ratio
    excess_daily = portfolio_df['returns'] - RF_DAILY
    sharpe = (excess_daily.mean() / portfolio_df['returns'].std()) * np.sqrt(252)

    # Max Drawdown
    cum = (1 + portfolio_df['returns']).cumprod()
    peak = cum.cummax()
    drawdown = (cum - peak) / peak
    max_dd = drawdown.min()

    return {
        'CAGR': cagr,
        'Volatility': vol,
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_dd
    }

# ─── 6. MAIN ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    def get_user_date(prompt):
        while True:
            s = input(prompt + " (YYYY-MM-DD): ")
            try:
                return datetime.strptime(s, '%Y-%m-%d')
            except ValueError:
                print("Invalid format. Please use YYYY-MM-DD.")

    print("Enter backtest date range:")
    start_date = get_user_date("Start date")
    end_date   = get_user_date("End date")
    if start_date >= end_date:
        print("Start must be before end.")
        exit()

    symbols_with_market = ASSET_SYMBOLS + [MARKET_SYMBOL]
    print("Fetching price data...")
    df_prices = fetch_closes(symbols_with_market, start_date, end_date)

    print("Computing signals...")
    signals, alphas = compute_signals(df_prices)

    print("Running backtest...")
    results = backtest_portfolio(df_prices, signals)

    # Print final results
    sv = results['total'].iloc[0]
    ev = results['total'].iloc[-1]
    total_ret = (ev / sv - 1)
    print(f"\nResult {start_date.date()} to {end_date.date()}")
    print(f"Start: ${sv:,.2f}, End: ${ev:,.2f}, Return: {total_ret*100:.2f}%")

    # Compute and print metrics
    metrics = compute_metrics(results)
    print("\nPerformance Metrics:")
    for k, v in metrics.items():
        if 'Ratio' in k:
            print(f"{k}: {v:.2f}")
        else:
            print(f"{k}: {v:.2%}")
'''
'''

## FOR BACKTESTING NEWS STRATEGY


import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from transformers import pipeline
import pytz

# ─── 1. CONFIGURE API ─────────────────────────────────────────────────────────
API_KEY = "PK3610I5ATPMJZF046XX"
API_SECRET = "1aLNghxvbEpB95n9hnECuqOofJDDdrczcfGGKdX3"
BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# ─── 2. FETCH OHLC DATA ──────────────────────────────────────────────────────
def fetch_bars(symbol, start_date, end_date):
    bars = api.get_bars(
        symbol,
        tradeapi.TimeFrame.Day,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        adjustment='raw',
        feed='iex'
    ).df

    if isinstance(bars.index, pd.MultiIndex):
        df = bars.xs(symbol, level=1).copy()
    else:
        df = bars.copy()

    df.index = pd.to_datetime(df.index)
    return df

# ─── 3. FETCH NEWS HEADLINES ─────────────────────────────────────────────────
def fetch_daily_sentiment(symbol, start_date, end_date, sentiment_model):
    current = start_date
    news_sentiment = {}

    while current <= end_date:
        day_start = current.strftime('%Y-%m-%dT00:00:00Z')
        day_end = current.strftime('%Y-%m-%dT23:59:59Z')

        try:
            news = api.get_news(symbol, start=day_start, end=day_end, limit=50)
        except Exception as e:
            print(f"Error fetching news for {current}: {e}")
            current += timedelta(days=1)
            continue

        if news:
            texts = [article.headline + ". " + (article.summary or "") for article in news]
            sentiments = sentiment_model(texts, truncation=True)
            # Average the sentiment scores for the day
            score = 0
            for s in sentiments:
                if s['label'] == 'POSITIVE':
                    score += 1
                elif s['label'] == 'NEGATIVE':
                    score -= 1
            score /= max(len(sentiments), 1)
            news_sentiment[current.date()] = score

        current += timedelta(days=1)

    return news_sentiment

# ─── 4. STRATEGY ─────────────────────────────────────────────────────────────
def sentiment_strategy(df, sentiment_scores, entry_threshold=0.5, exit_threshold=-0.2, initial_capital=100_000):
    df = df.copy()
    df['signal'] = 0

    for idx in df.index:
        score = sentiment_scores.get(idx.date(), 0)
        if score >= entry_threshold:
            df.at[idx, 'signal'] = 1
        elif score <= exit_threshold:
            df.at[idx, 'signal'] = 0
        else:
            df.at[idx, 'signal'] = np.nan

    df['signal'] = df['signal'].ffill().fillna(0)
    df['position'] = df['signal'].diff()

    cash = initial_capital
    shares = 0
    history = []

    for dt, row in df.iterrows():
        price = row['close']
        if row['position'] == 1:  # Buy
            shares = cash // price
            cash -= shares * price
        elif row['position'] == -1 and shares > 0:  # Sell
            cash += shares * price
            shares = 0
        total = cash + shares * price
        history.append({'date': dt, 'total': total, 'sentiment': sentiment_scores.get(dt.date(), 0)})

    return pd.DataFrame(history).set_index('date')

# ─── 5. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    symbol = 'TSLA'

    # Input custom backtest range
    try:
        start_input = input("Enter START date (YYYY-MM-DD): ")
        end_input = input("Enter END date (YYYY-MM-DD): ")
        start_date = datetime.strptime(start_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_input, "%Y-%m-%d")
        if start_date > end_date:
            raise ValueError("Start date must be before end date.")
    except Exception as e:
        print(f"Invalid date input: {e}")
        exit()

    print("\nLoading sentiment model...")
    sentiment_model = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

    print(f"\nFetching price data for {symbol}...")
    bars = fetch_bars(symbol, start_date, end_date)

    print(f"Fetching news sentiment between {start_date.date()} and {end_date.date()}...")
    sentiment_scores = fetch_daily_sentiment(symbol, start_date, end_date, sentiment_model)

    print("Running backtest...")
    results = sentiment_strategy(bars, sentiment_scores)

    start_val = results['total'].iloc[0]
    end_val = results['total'].iloc[-1]
    print(f"\nStart Portfolio: ${start_val:,.2f}")
    print(f"End Portfolio:   ${end_val:,.2f}")
    print(f"Sentiment Strategy Return: {((end_val/start_val - 1)*100):.2f}%")
'''
