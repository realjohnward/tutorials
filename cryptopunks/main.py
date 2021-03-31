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
        try:
            img_url = resp['image_url']
            results.append(f'<img src="{img_url}" width=100 height=100 />')
        except:
            results.append(None)
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

def txn_hashes_to_txn_links(txn_hashes):
    return [f'<a href="https://etherscan.io/tx/{Txn}">{Txn[:20]}...</a>' for Txn in txn_hashes]

def get_punk_sales(ids, ethers):
    punk_sales = {}
    for id, ether in zip(ids, ethers):
        if id not in punk_sales:
            punk_sales[id] = ether 
        else:
            punk_sales[id] += ether 
    
    results = []
    for id in ids:
        results.append(punk_sales[id])

    return results 


ids = [6000 + i for i in range(20)]
records = []
for id in ids:
    event_filter = contract.events.PunkBought.createFilter(fromBlock=0, toBlock=latest_block_number, argument_filters={'punkIndex': id})
    for event in event_filter.get_all_entries():
        receipt = w3.eth.waitForTransactionReceipt(event['transactionHash'])
        data = contract.events.PunkBought().processReceipt(receipt)[0]
        print(data)
        record = {'Txn': data['transactionHash'].hex(), 'ID': data['args']['punkIndex'], 'Value': data['args']['value'], 'Block': data['blockNumber']}
        records.append(record)

print(len(records))

df = pd.DataFrame.from_records(records)
# df['Value'] = df['Value'].astype(float)
df['Ether'] = weis_to_ethers(df['Value'])
df['Image'] = get_img(df['ID'])
df['Datetime'] = blocks_to_datetimes(df['Block'])
df['Txn'] = txn_hashes_to_txn_links(df['Txn'])

# gb = df.groupby('ID')
# nft_dfs = [gb.get_group(g) for g in gb.groups]
df['TotalMarketSales'] = df['Ether'].sum()
df['TotalSales'] = get_punk_sales(df['ID'],df['Ether'])
df['MarketShare'] = df['TotalSales'] / df['TotalMarketSales']
print(df.to_dict(orient='records'))
df['AvgPctChange'] = df.groupby('ID')['Ether'].pct_change()
df.drop_duplicates("ID", inplace=True)


snippets = []

# for nft_df in nft_dfs:
# ax = df.plot(x='Datetime', y='Ether')
# chart_html = chart(ax, w=300, h=300)
df_html = df.to_html(columns=['Image','ID','TotalSales', 'MarketShare', 'AvgPctChange'], escape=False, index=False)
# snippets.append(f'{chart_html}<br/>{df_html}')
snippets.append(df_html)

# market_share_ax = df.drop_duplicates('ID').plot.pie(y='TotalSales', x='ID', figsize=(5, 5), xlabel='NFT')
# ms_snippet = chart(market_share_ax, w=300, h=300)

with open("output.html", "w") as f:
    f.write('<hr><br/>'.join(snippets))
    f.close()

webbrowser.open("output.html")
