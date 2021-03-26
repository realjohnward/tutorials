import pandas as pd 
from web3 import Web3 
import matplotlib.pyplot as plt 
import json 
import requests 
import webbrowser
from datetime import datetime 
from io import BytesIO
from base64 import b64encode 

mainnet_url = 'https://mainnet.infura.io/v3/4113c5a1275a4c1093487f9d7f74edd3'

w3 = Web3(Web3.HTTPProvider(mainnet_url))

contract_addr = '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB'

abi = json.load(open("abi.json"))

contract = w3.eth.contract(contract_addr, abi=abi)

latest_block_number = w3.eth.get_block('latest')['number']

event_filter = contract.events.PunkBought.createFilter(fromBlock=0, toBlock=latest_block_number, argument_filters={'punkIndex': 7804})

records = []

def chart(ax, w=100, h=100):
    if ax:
        buf = BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        img_html = f'<img width={w} height={h} src="data:image/png;base64,{b64encode(buf.getvalue()).decode()}" />'
        return img_html 
    else:
        return "--"

def get_img(ids):
    results = []
    for id in ids:
        url = f'https://api.opensea.io/api/v1/asset/{contract_addr}/{id}'
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        img_url = resp['image_url']
        results.append(f'<img src="{img_url}" width=100 height=100 />')
    return results 

def weis_to_ethers(weis):
    results = []
    for wei in weis:
        results.append(float('%.20f' % w3.fromWei(wei, 'ether')))
    return results 

def blocks_to_datetimes(blocks):
    results = []
    for b in blocks:
        ts = w3.eth.get_block(b).timestamp 
        results.append(datetime.fromtimestamp(ts))
    return results 

for event in event_filter.get_all_entries():
    receipt = w3.eth.waitForTransactionReceipt(event['transactionHash'])
    data = contract.events.PunkBought().processReceipt(receipt)[0]
    print(data)
    record = {'ID': data['args']['punkIndex'], 'Value': data['args']['value'], 'Block': data['blockNumber']}
    records.append(record)

print(len(records))

df = pd.DataFrame.from_records(records)
# df['Value'] = df['Value'].astype(float)
df['Ether'] = weis_to_ethers(df['Value'])
df['Image'] = get_img(df['ID'])
df['Datetime'] = blocks_to_datetimes(df['Block'])

ax = df.plot(x='Datetime', y='Ether')
chart_html = chart(ax, w=300, h=300)

df_html = df.to_html(columns=['Image', 'ID', 'Ether'], escape=False)

with open("output.html", "w") as f:
    f.write(f'<html><head></head><body>{chart_html}<br/>{df_html}</body></html>')
    f.close()

webbrowser.open("output.html")
