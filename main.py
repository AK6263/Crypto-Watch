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

def getbalance():
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

    for i in data:
        if i['balance'] != '0.0':
            print(i)
    #print(data)

getbalance()

def currentPrice(base):
    url = common_url + "/ticker"
    response = requests.get(url)
    data = response.json()

    res = {}
    for j in data:
        if j['market'] in base:
            res[j['market']] = [j['timestamp'],j['last_price']]
    return res

coins = ['BTC','ETH','COMP','LINK','ADA']
base = ['BTCINR','ETHINR','COMPETH','LINKINR','ADAINR']
df = pd.DataFrame({
    'COINS' : coins,
    'BASE' : base,
    'MARKET PRICE' : [0,0,0,0,0],
    'BALANCE' : [0,0,0,0,0],
    'TIMESTAMP' : [0,0,0,0,0],
    'CONV RATE' : [0,0,0,0,0],
    'TOTAL' : [0,0,0,0,0],
    'INITIAL' : [0,0,0,0,0],
    'DAILY PROFIT' : [0,0,0,0,0],
    'TOTAL PROFIT' : [0,0,0,0,0],
})

MARKET_PRICE = currentPrice(base)
df['MARKET PRICE'] = [float(MARKET_PRICE[i][1]) for i in df['BASE']]
df['MARKET PRICE'] = df['MARKET PRICE'].apply(lambda x: '%.6f' % x)
df['TIMESTAMP'] = [datetime.fromtimestamp(MARKET_PRICE[i][0]) for i in df['BASE']]
bal,inrwallet = getbalance(coins)
df['BALANCE'] = [float(bal[i]) for i in df['COINS']]
df['BALANCE'] = df['BALANCE'].apply(lambda x: '%.14f' % x)
convrate = []
for i in base:
    if 'INR' not in i:
        b = 0
        for j in base:
            if j[:3] == i[-3:]:
                b = float(MARKET_PRICE[j][1])
        convrate.append(1/(float(MARKET_PRICE[i][1])*b))
    else:
        convrate.append(1)
df['CONV RATE'] = convrate
df['TOTAL'] = df['BALANCE'].astype(float)*df['MARKET PRICE'].astype(float)*df['CONV RATE']
df['TOTAL'] = df['TOTAL'].apply(lambda x: '%.8f' % x)
df['TOTAL PROFIT'] = df['TOTAL'].astype(float) - df['INITIAL']
print('The Net Profit = ',df['TOTAL PROFIT'].sum())
print()
# print(df.dtypes)

df['TOTAL'] = df['TOTAL'].astype(float)
# df.groupby(['BASE']).sum().plot(kind='pie',subplots=True, y='INITIAL')
# df.groupby(['BASE']).sum().plot(kind='pie',subplots=True, y='TOTAL')
#plot = plt.figure(1)
#plt.pie(df['TOTAL'],labels=df['BASE'])
#plt.title('TOTAL CURRENT')
#plot = plt.figure(2)
#plt.pie(df['INITIAL'],labels=df['BASE'])
#plt.title('TOTAL INITIAL')
#plot = plt.figure(3)

total = df['TOTAL'].astype(float)
initial = df['INITIAL'].astype(float)
diff = df['TOTAL PROFIT']
x = df['BASE']

for i, v in enumerate(initial):
    plt.text(i + 0.4, v + 0.01, str(v),rotation=60)
for i, v in enumerate(diff):
    plt.text(i + 0.6, v + initial[i] - 0.01, str(round(initial[i]+diff[i],4)) +" ("+ str(round(v,4)) + ")",rotation=60)
#plt.ylim(0,initial.max() + 1000)
#plt.bar(x,initial,color='gray')
diffp = [0,0,0,0,0]
for i in range(len(diff)):
    if diff[i] >= 0:
        diffp[i] = diff[i]
        diff[i] = 0
#plt.bar(x,diff,bottom=initial,color='r')
#plt.bar(x,diffp,bottom=initial,color='g')
# Create a new data base to save the profits
if not os.path.exists("./log.csv"):
    log = pd.DataFrame({
        "TIMESTAMP" : [],
    })
    for i in df['BASE']:
        log[i] = []
    for i in df['BASE']:
        log[i + " PROFIT"] = []
    # log['INITIAL'] = []
    log['NET PROFIT'] = []
else:
    log = pd.read_csv('./log.csv')

ser = {}
Logger = pd.DataFrame()
ser['TIMESTAMP'] = df['TIMESTAMP'].tolist()[0]
print(type(df['TIMESTAMP'].tolist()[0]))
for i in df['BASE']:
    ser[i] = df[df['BASE'] == i]['TOTAL'].tolist()[0]
    ser[i + " PROFIT"] = df[df['BASE'] == i]['TOTAL PROFIT'].tolist()[0]

ser["NET PROFIT"] = df['TOTAL PROFIT'].sum()
log = log.append(ser,ignore_index = True)
log['TIMESTAMP'] = pd.to_datetime(log['TIMESTAMP'])

#plot = plt.figure(4)
#plt.plot(log['TIMESTAMP'],log['NET PROFIT'],'b-')
#plt.plot(log['TIMESTAMP'],log['NET PROFIT'],'rx')
#plt.xlabel('TIMESTAMP')#
#plt.ylabel('NET PROFIT')
#plt.xticks(rotation=30)
# print(log)
print(df)
# show(df,log)
df.to_csv('./current_data.csv',index=False)
log.to_csv('./log.csv',index=False)
#plt.show()
