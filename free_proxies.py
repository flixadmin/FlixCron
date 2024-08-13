import asyncio, aiohttp, requests
from aiohttp_proxy import ProxyConnector
from bs4 import BeautifulSoup

def geonode_proxies():
    all_pr = ''
    countries = []
    ct = '&'.join(['country=' + i for i in countries])
    try:
        for i in range(1,3):
            resp = requests.get(f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={i}&sort_by=lastChecked&sort_type=desc&'+ct, headers={'Origin': 'https://geonode.com'})
            data = resp.json()['data']
            for item in data:
                for prt in item['protocols']:
                    pr = prt + '://' + item['ip'] + ':' + item['port']
                    all_pr += pr + '\n'
    except:
        import traceback
        print(traceback.format_exc())
    return all_pr

def fpl_proxies():
    resp = requests.get('https://free-proxy-list.net/')
    soap = BeautifulSoup(resp.text, 'html.parser')
    ta = soap.select_one('textarea')
    ta_text = ta.text.split('\n')[3:]
    return 'http://' + '\n'.join(ta_text).strip().replace('\n' ,'\nhttp://') + '\n'

def psProxies():
    r = requests.get('https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text&timeout=20000')
    pl = r.text.replace('\r\n','\n')
    return pl

async def isValidProxy(pr):
    url = 'http://pixeldrain.com'
    contains = 'stats.pixeldrain.com'
    connector = ProxyConnector.from_url(pr)
    try:
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.get(url, timeout=20) as r:
                if r.status == 200 and contains in await r.text():
                    return pr
    except:
        pass
    return False

async def getWorkingProxies(pr_text:str):
    working_pr = []
    t = [isValidProxy(k) for k in pr_text.strip().split('\n')]
    for task in asyncio.as_completed(t):
        d = await task
        if d: working_pr.append(d)
    return working_pr

all_pr = psProxies()
all_pr += fpl_proxies()
all_pr += geonode_proxies()

all_proxies = all_pr.strip().split('\n')
working_proxies = lambda: asyncio.run(getWorkingProxies(all_pr))

if __name__ == '__main__':
    pr_list = working_proxies()
    from json import dumps
    open('pr.json', 'w').write(dumps(pr_list, indent=2))