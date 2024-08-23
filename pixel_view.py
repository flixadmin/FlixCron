from websockets_proxy import Proxy, proxy_connect
from aiohttp_proxy import ProxyConnector
import asyncio, free_proxies, random, aiohttp, traceback
from websockets import connect

user_agents = open('ua.txt').readlines()
random_ua = lambda: random.choice(user_agents).strip()

async def view_pixel_drain(file_id, proxy_url=None):
    # async with aiohttp.ClientSession(connector=ProxyConnector.from_url(proxy_url)) as s:
    #     async with s.get('http://pixeldrain.com/u/' + file_id) as r:
    #         await r.text()
    wc = connect
    kwargs = dict()
    if proxy_url:
        wc = proxy_connect
        kwargs = dict(proxy=Proxy.from_url(proxy_url))
    async with wc("wss://pixeldrain.com/api/file_stats",
                    origin='https://pixeldrain.com',
                    user_agent_header=random_ua(),
                    extra_headers={'Cookie': 'pd_auth_key=83jdid8d83iejd8e84udh73'},
                    **kwargs) as websocket:
        await websocket.send('{"type":"file_stats","data":{"file_id":"' + file_id + '"}}')
        message = await asyncio.wait_for(websocket.recv(), 60)
        print(f"Received: {message.strip()}", flush=True)

async def run_with_proxies(file_id, proxy_list):
    t = [view_pixel_drain(file_id, l) for l in proxy_list]
    for task in asyncio.as_completed(t):
        try:
            await task
        except asyncio.TimeoutError: pass
        except Exception as err:
            pass
            print(traceback.format_exc(), flush=True)

async def run_all_with_proxies(file_ids:list, proxy_list:list):
    t = [run_with_proxies(p, proxy_list) for p in file_ids]
    for task in asyncio.as_completed(t):
        await task

if __name__ == '__main__':
    print('Started')
    print(len(free_proxies.all_proxies))
    asyncio.run(run_with_proxies('YSApALVk', free_proxies.all_proxies))
