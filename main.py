import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import hmac
import hashlib
import base64
import json
import time
import requests
import os
from datetime import datetime
# from pandasgui import show
# Uncomment the following comment to display in non-scientific format
# pd.set_option('display.float_format', '{:.2f}'.format)
coindcx = json.load(open('./api.json'))

key = coindcx['apikey']
secret = coindcx['secretkey']

common_url = "https://api.coindcx.com/exchange"

def get_portfolio():
    secret_bytes = bytes(secret, encoding='utf-8')
    timeStamp = int(round(time.time() * 1000))
    body = {
        "timestamp": timeStamp
    }
    json_body = json.dumps(body, separators = (',', ':'))
    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()
    url = common_url + "/v1/users/balances"
    ret = {}
    headers = {
    'Content-Type': 'application/json',
    'X-AUTH-APIKEY': key,
    'X-AUTH-SIGNATURE': signature
    }
    response = requests.post(url, data = json_body, headers = headers)
    data = response.json()

    p = [i for i in data if float(i['balance']) != 0.0]
    portfolio = pd.DataFrame(p,index=[i['currency'] for i in p])

    inr = portfolio[portfolio['currency'] == 'INR']['balance'].values[0]
    usdt = portfolio[portfolio['currency'] == 'USDT']['balance'].values[0]
    portfolio = portfolio.drop(['INR','USDT'])

    return portfolio,inr,usdt

def currentPrice(portfolio):
    coins = list(portfolio['currency'])
    base = [i+'USDT' for i in coins]

    url = common_url + "/ticker"
    response = requests.get(url)
    data = response.json()
    prices = {}
    usdtinr = 0
    for i in data:
        if i['market'] in base:
            prices[i['market']] = float(i['last_price'])
        elif i['market'] == 'USDTINR':
            usdtinr = float(i['last_price'])

    return prices, coins, base, usdtinr


portfolio,inr,usdt = get_portfolio()
prices,coins,base,usdtinr = currentPrice(portfolio)

# print(portfolio)
# print(prices)


df = pd.DataFrame({
    'COINS' : coins,
    'BASE' : base,
    'MARKET PRICE (INR)' : [usdtinr*prices[i + 'USDT'] for i in coins],
    'BALANCE' : portfolio['balance'].astype(float),
    # 'TIMESTAMP' : [0,0,0,0,0],
    # 'CONV RATE' : [0,0,0,0,0],
    # 'TOTAL' : [0.0 for i in range(len(coins))] ,
    # 'INITIAL' : [0,0,0,0,0],
    # 'DAILY PROFIT' : [0,0,0,0,0],
    # 'TOTAL PROFIT' : [0,0,0,0,0],
})
df['TOTAL'] = df['MARKET PRICE (INR)'] * df['BALANCE']
print(df.to_string(index=False))
print("USDTINR : {}, INR : {}, USDT : {}, TOTAL_HOLD : {} ".format(usdtinr,inr,usdt,df['TOTAL'].sum()+float(inr)))

# uncomment the following code to reset to the scientific notation option
# pd.reset_option('all')
