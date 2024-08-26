import asyncio, aiohttp, vars, random, base64
from helper import send_mail

js_snippet = lambda ids: """
function viewAllPixelDrain(ids) {
  return new Promise((resolve, reject) => {
    let socket = new WebSocket("wss://pixeldrain.com/api/file_stats");
    let msg_count = 0;
    let init = (s) => {
      s.onopen = async function (e) {
        for (let i = 0; i < ids.length; i++) {
          let id = ids[i];
          let messageString = '{"type":"file_stats","data":{"file_id":"' + id + '"}}';
          s.send(messageString);
        }
      };
      s.onmessage = async function (d) {
        msg_count++;
        if (msg_count => ids.length) {
          s.close();
          resolve(JSON.parse(d.data));
        }
      }
      s.onerror = function (e) {reject(e)};
      setTimeout(function(){reject('Timeout Error')}, 10000);
    }
    init(socket);
  });
}
var proms = [];
for (var i = 0; i < 50 ; i ++) {
  proms.push(viewAllPixelDrain(%s));
};
await Promise.all(proms);
""" % str(ids)

async def async_get(*args, **kwargs):
    async with aiohttp.ClientSession() as s:
        async with s.get(*args, **kwargs) as r:
            await r.text()
            return r

async def get_key(min_credit:int = 50, send_mail_on_invalid:bool=False, send_mail_on_no_credit_at_all:bool=False):
    tasks = [async_get('https://api.scrapingant.com/v2/usage', params={'x-api-key': key}) for key in vars.API_KEYS]
    keys = {}
    for task in asyncio.as_completed(tasks):
        r = await task
        d = await r.json()
        k = r.url.query.get('x-api-key')
        keys[k] = d.get('remained_credits')

    valids = [k for k, v in keys.items() if not v is None and v >= min_credit]
    invalids = [k for k, v in keys.items() if v is None]
    if invalids and send_mail_on_invalid:
        send_mail('FlixCron: These Scraping Ant API Keys are seems to be invalid', 'Keys:<br>' + '<br>'.join([f'{i+1}. {u}' for i, u in enumerate(invalids)]))
    if not valids:
        if send_mail_on_no_credit_at_all and len(vars.API_KEYS) != len(invalids):
            send_mail('FlixCron: No api key has enough credits', 'Keys:<br>' + '<br>'.join([f'{i+1}. {u}' for i, u in enumerate(vars.API_KEYS)]))
        raise Exception('Required Credit not Available in Scraping Ant')
    return random.choice(valids)

async def send_views_to_pixel_ids(file_ids:list, reqs:int=3):
    key = await get_key(reqs * 10, True)
    url = 'https://api.scrapingant.com/v2/general?url=https%3A%2F%2Fexample.com&x-api-key=7b9d550345e24a679bface5bdd9ff833&js_snippet=ZG9jcw=='
    params = {'url': 'https://pixeldrain.com/u/' + random.choice(file_ids), 'x-api-key': key, 'js_snippet': base64.b64encode(js_snippet(file_ids).encode()).decode()}
    for _ in range(reqs):
        r = await async_get(url, params=params)
        if r.status != 200:
            print('Error in Scraping Ant. Status:', r.status, 'Resp:', await r.text(), flush=True)
    

if __name__ == '__main__':
    asyncio.run(send_views_to_pixel_ids(['E7zh9LH1', '2N33Ff4Z', 'iLQrBDSo']))
