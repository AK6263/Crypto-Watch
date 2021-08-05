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
from pandasgui import show

coindcx = json.load(open('./api.json'))

key = coindcx['apikey']
secret = coindcx['secretkey']

common_url = "https://api.coindcx.com/exchange"

def getportfolio():
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
    #for i in data:
    #    if i['currency'] in coins:
    #        ret[i['currency']] = i['balance']
    #inrval = [i['balance'] for i in data if i['currency'] == 'INR']
    #return ret,inrval[0]
    p = []
    for i in data:
        if i['balance'] != '0.0':
            p.append(i)

    portfolio = pd.DataFrame(p)
    print(portfolio)
    #return portfolio
    coins = list(portfolio['currency'])
    coins.remove('USDT')
    a = 'USDT'
    #print(coins)
    base = coins[:]
    for i in range(len(coins)):
        base[i] = ''.join((base[i],a))

    #print(base)
    url = common_url + "/ticker"
    response = requests.get(url)
    data = response.json()
    #print(data)

    res = {}
    for j in data:
        if j['market'] in base:
            res[j['market']] = j['last_price']
    #print(res)


getportfolio()
