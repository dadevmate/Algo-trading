

## FOR IBKR LIVE MARKET TRADING

import yfinance as yf
import numpy as np
import pandas as pd
import random
import time
from ib_insync import *

while True:

   

# Connect to IB Gateway or TWS
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)  # port 7497 for TWS paper, 7496 for TWS live, 4002 for IB Gateway

   

    
        
    def get_dividend_yield(ticker):
        """
        Fetches the current dividend yield for a given ticker.
        Returns 0.0 if no dividend is found.
        """
        info = yf.Ticker(ticker).info
        # 'dividendYield' is returned as a decimal (e.g. 0.018 for 1.8%)
        return info.get('dividendYield') or 0.0

    def get_return_on_equity(ticker):
        """
        Fetches the current dividend yield for a given ticker.
        Returns 0.0 if no dividend is found.
        """
        info = yf.Ticker(ticker).info
        # 'dividendYield' is returned as a decimal (e.g. 0.018 for 1.8%)
        return info.get('returnOnEquity') or 0.0


    def get_earnings(ticker):
        """
        Fetches the current dividend yield for a given ticker.
        Returns 0.0 if no dividend is found.
        """
        info = yf.Ticker(ticker).info
        # 'dividendYield' is returned as a decimal (e.g. 0.018 for 1.8%)
        return info.get('earningsQuarterlyGrowth') or 0.0

    def get_fifty(ticker):
        """
        Fetches the current dividend yield for a given ticker.
        Returns 0.0 if no dividend is found.
        """
        info = yf.Ticker(ticker).info
        # 'dividendYield' is returned as a decimal (e.g. 0.018 for 1.8%)
        return info.get('fiftyDayAverageChangePercent') or 0.0

    def get_twoHundred(ticker):
        """
        Fetches the current dividend yield for a given ticker.
        Returns 0.0 if no dividend is found.
        """
        info = yf.Ticker(ticker).info
        # 'dividendYield' is returned as a decimal (e.g. 0.018 for 1.8%)
        return info.get('twoHundredDayAverageChangePercent') or 0.0

    def get_target(ticker):
        """
        Fetches the current dividend yield for a given ticker.
        Returns 0.0 if no dividend is found.
        """
        info = yf.Ticker(ticker).info
        
        # 'dividendYield' is returned as a decimal (e.g. 0.018 for 1.8%)
        return info.get("analyst_price_targets") or 0.0

    # --- CONFIGURE YOUR TICKERS HERE ---



    sp500_tickers = [
        'MMM','AOS','ABT','ABBV','ACN','ATVI','ADM','ADBE','ADP','AAP',
        'AES','AFL','A','APD','AKAM','ALK','ALLE','MO','AMZN','AEE',
        'AAL','AEP','AXP','AIG','AMT','AMP','ABC','AME','AMGN','APH',
        'ADI','ANSS','ANTM','AON','APA','AAPL','AMAT','APTV','ACGL','ADM',
        'ANET','AJG','AIZ','T','ATO','ADSK','ADP','AZO','AVB','AVY',
        'AXON','BKR','BALL','BAC','BAX','BDX','BBY','BIIB','BLK','BK',
        'BA','BKNG','BWA','BXP','BSX','BHF','BMY','AVGO','BR','BRK.B',
        'BF.B','CHRW','COG','CDNS','CPB','COF','CAH','KMX','CCL','CAT',
        'CBOE','CBRE','CDW','CE','CNC','CNP','CERN','CF','SCHW','CHTR',
        'CVX','CMG','CB','CHD','CI','CINF','CTAS','CSCO','C','CFG',
        'CTXS','CLX','CME','CMS','COO','COP','STZ','CPRT','GLW','COST',
        'COTY','CCI','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE',
        'DAL','XRAY','DVN','DXCM','FANG','DLR','DFS','DISCA','DISCK','D',
        'DPZ','DOV','DOW','DTE','DUK','DRE','DD','DXC','EMN','ETN',
        'EBAY','ECL','EIX','EW','EA','EMR','ETR','EOG','EFX','EQIX',
        'EQR','ESS','EL','ETSY','RE','EVRG','ES','EXC','EXPE','EXPD',
        'EXR','XOM','FFIV','FB','FAST','FRT','FDX','FIS','FITB','FE',
        'FRC','FISV','FLT','FLIR','FLS','FMC','F','FTNT','FTV','FBHS',
        'FOXA','FOX','BEN','FCX','GPS','GRMN','IT','GD','GE','GIS',
        'GM','GPC','GILD','GL','GPN','GS','GT','GWW','HAL','HBI',
        'HIG','HAS','HCA','PEAK','HSIC','HSY','HES','HPE','HLT','HOLX',
        'HD','HON','HRL','HST','HWM','HPQ','HUM','HBAN','HII','IEX',
        'IDXX','INFO','ITW','ILMN','INCY','IR','INTC','ICE','IBM','IFF',
        'INTU','ISRG','IVZ','IP','IPG','IQV','IRM','JKHY','J','JBHT',
        'SJM','JNJ','JCI','JPM','JNPR','KSU','K','KEY','KEYS','KMB',
        'KIM','KMI','KLAC','KHC','KR','LB','LHX','LH','LRCX','LW',
        'LVS','LEG','LDOS','LEN','LLY','LNC','LIN','LYV','LKQ','LMT',
        'L','LOW','LUMN','LYB','MTB','MRO','MPC','MKTX','MAR','MMC',
        'MLM','MAS','MA','MKC','MXIM','MCD','MCK','MDT','MRK','MET',
        'MTD','MGM','MCHP','MU','MSFT','MAA','MHK','TAP','MDLZ','MPWR',
        'MNST','MCO','MS','MOS','MSI','MSCI','NDAQ','NTAP','NFLX','NWL',
        'NEM','NWSA','NWS','NEE','NLSN','NKE','NI','NSC','NTRS','NOC',
        'NLOK','NCLH','NRG','NUE','NVDA','NVR','NXPI','ORLY','OXY','ODFL',
        'OMC','OKE','ORCL','OTIS','PCAR','PKG','PH','PAYX','PAYC','PYPL',
        'PNR','PBCT','PEP','PKI','PRGO','PFE','PM','PSX','PNW','PXD',
        'PNC','PPG','PPL','PFG','PG','PGR','PLD','PRU','PTC','PEG',
        'PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','RL','RJF','RTX',
        'O','REG','REGN','RF','RSG','RMD','RHI','ROK','ROL','ROP',
        'ROST','RCL','SPGI','CRM','SBAC','SLB','STX','SEE','SRE','SHW',
        'SPG','SWKS','SLG','SNA','SO','LUV','SPH','SWK','SBUX','STT',
        'STE','SYK','SIVB','SYF','SNPS','SYY','TMUS','TGT','TEL','TDY',
        'TFX','TER','TSLA','TXN','TXT','TMO','TJX','TSCO','TT','TDG',
        'TRV','TRMB','TFC','TWTR','TYL','TSN','UDR','ULTA','USB','UAA',
        'UA','UNP','UAL','UNH','UPS','URI','UHS','VLO','VTR','VRSN',
        'VRSK','VZ','VRTX','V','VNO','VMC','WRB','WAB','WMT','WCG',
        'WELL','WST','WDC','WU','WRK','WY','WHR','WMB','WLTW','WYNN',
        'XEL','XLNX','XYL','YUM','ZBRA','ZBH','ZION','ZTS'
    ]

    tickers = [random.choice(sp500_tickers), random.choice(sp500_tickers)]

    # Fetch dividend yields
    yields = {t: get_dividend_yield(t) for t in tickers}
    returnOnEquity = {t: get_return_on_equity(t) for t in tickers}
    earnings = {t: get_earnings(t) for t in tickers}
    fifty = {t: get_fifty(t) for t in tickers}
    twoHundred = {t: get_twoHundred(t) for t in tickers}
    target = {t: get_target(t) for t in tickers}


    # Compare
    t1, t2 = tickers

    y1, y2 = yields[t1], yields[t2]
    r1, r2 = returnOnEquity[t1], returnOnEquity[t2]
    e1, e2 = earnings[t1], earnings[t2]
    f1, f2 = fifty[t1], fifty[t2]
    th1, th2 = twoHundred[t1], twoHundred[t2]
    tar1, tar2 = target[t1], target[t2]


    score1 = 0
    score2 = 0
    if y1 > y2:
        score1 += 1
    elif y2 > y1:
        score2 += 1
    else:
        score1 += 1
        score2 += 1

    if tar1 > tar2:
        score1 += 1
    elif tar2 > tar1:
        score2 += 1
    else:
        score1 += 1
        score2 += 1


    if e1 > e2:
        score1 += 1
    elif e2 > e1:
        score2 += 1
    else:
        score1 += 1
        score2 += 1
    ## go

    if f1 > f2:
        score1 += 1
    elif f2 > f1:
        score2 += 1
    else:
        score1 += 1
        score2 += 1

    if th1 > th2:
        score1 += 1
    elif th2 > th1:
        score2 += 1
    else:
        score1 += 1
        score2 += 1

    if r1 > r2:
        score1 += 1
    elif r2 > r1:
        score2 += 1
    else:
        score1 += 1
        score2 += 1

 
    if score1 > score2:
        print(f"{t1} is a better deal than {t2}")
        contract = Stock(t1, 'SMART', 'USD')
        current_price = yf.Ticker(t1).history(period='1d')['Close'].iloc[-1]
        order = LimitOrder('BUY', 1, current_price)
        trade = ib.placeOrder(contract, order)
        ib.sleep(1)
        while not trade.isDone():
            ib.sleep(0.5)
        print("Order filled:", trade.orderStatus.status)

    elif score2 > score1:
        print(f"{t2} is a better deal than {t1}")

        contract = Stock(t2, 'SMART', 'USD')
        current_price = yf.Ticker(t2).history(period='1d')['Close'].iloc[-1]
        order = LimitOrder('BUY', 1, current_price)
        trade = ib.placeOrder(contract, order)
        ib.sleep(1)
        while not trade.isDone():
            ib.sleep(0.5)
        print("Order filled:", trade.orderStatus.status)



    else:
        print("They are both good deals")
        contract = Stock(t1, 'SMART', 'USD')
        current_price = yf.Ticker(t1).history(period='1d')['Close'].iloc[-1]
        order = LimitOrder('BUY', 1, current_price)
        trade = ib.placeOrder(contract, order)
        ib.sleep(1)
        while not trade.isDone():
            ib.sleep(0.5)
        print("Order filled:", trade.orderStatus.status)
        
        contract = Stock(t2, 'SMART', 'USD')
        current_price = yf.Ticker(t2).history(period='1d')['Close'].iloc[-1]
        order = LimitOrder('BUY', 1, current_price)
        trade = ib.placeOrder(contract, order)
        ib.sleep(1)
        while not trade.isDone():
            ib.sleep(0.5)
        print("Order filled:", trade.orderStatus.status)
    
    ib.disconnect()

    time.sleep(30)



