import time
import pyupbit
import datetime

access = "your-access"
secret = "your-secret"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 매도가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_bid_price(ticker):
    """현재 매수가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["bid_price"]

def cur_price(ticker):
    """현재 체결가 조회"""
    return pyupbit.get_current_price(ticker)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

transaction=0
avg_price=0
k=0.3
sp=0.97
target_coin=[]
t_coin=[]
tops = ['KRW-ETH', 'KRW-ADA', 'KRW-XRP', 'KRW-DOT', 'KRW-DOGE', 'KRW-BTC']

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            if transaction == 0:
                target_price=[]
                current_price=[]
                comp=[] 
                for n in tops:
                    target = get_target_price(n, k)
                    target_price.append(target)
                    current = get_current_price(n)
                    current_price.append(current)
                    comp.append(target < current)

                if any(comp):  
                    buying=[]
                    for i in list(np.where(comp)[0]):
                        val = pyupbit.get_ohlcv(tops[i], interval="day", count=1)
                        buying.append((tops[i], val.iloc[0]['value']))
                    sorted_buying = sorted(buying, key=lambda x:x[1], reverse=True)
                    target_coin=sorted_buying[0][0]
                    t_coin=target_coin[4:]
                    krw = get_balance("KRW")
                    if krw > 5000:
                        upbit.buy_market_order(target_coin, krw*0.9995)
                        transaction = 1    
                        avg_price = upbit.get_balance(target_coin)['avg_buy_price']          
    
            elif transaction == 1:
                curr_price = cur_price(target_coin)    
                if curr_price < (avg_price * sp):
                    coin_val = get_balance(t_coin)
                    if coin_val > (5000/curr_price): 
                        upbit.sell_market_order(target_coin, coin_val*0.9995)  
                        transaction=0
 
        else:
            coin_val = get_balance(t_coin)
            if coin_val > (5000/curr_price): 
                upbit.sell_market_order(target_coin, coin_val*0.9995)  
            transaction=0
            avg_price=0
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
