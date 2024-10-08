import psycopg2, vars, time, aiohttp, re, json, asyncio, random, requests, traceback
from datetime import datetime, timezone
from json import loads
from websockets import connect

user_agents = open('ua.txt').readlines()
random_ua = lambda: random.choice(user_agents).strip()

def days_from_now(time_str):
    try:
        return (datetime.now(timezone.utc) - datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)).days
    except:
        return (datetime.now(timezone.utc) - datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)).days

def send_mail(subject:str, body:str):
    try:
        r = requests.post(vars.MAIL_URI, data={'s': subject, 'b': body})
        if not r.json()['success']:
            raise Exception('Cannot send email. View server logs.')
    except:
        print(traceback.format_exc(), flush=True)

def getLinkRows(last_updated_day_ago : int = 0):
    before_time = int(time.time() / 60) - last_updated_day_ago * 24 * 60
    conn = psycopg2.connect(vars.FW_DB_URI)
    cur = conn.cursor()
    cur.execute(f'SELECT id, url, CAST(last_visit AS INTEGER) FROM "link" WHERE CAST(last_visit AS INTEGER) < {before_time}')
    columns = [desc[0] for desc in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows.copy()

def updateLinkRows(rows:list):
    if not rows:
        return print('No rows to given to update', flush=True)
    conn = psycopg2.connect(vars.FW_DB_URI)
    cur = conn.cursor()
    values = ", ".join([f"({row['id']}, '{row['last_visit']}')" for row in rows])
    query = f"""
    UPDATE "link"
    SET last_visit = v.last_visit
    FROM (VALUES {values}) v(id, last_visit)
    WHERE v.id = link.id
    """
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

async def getViewsOfPixelFile(file_id:str):
    async with connect("wss://pixeldrain.com/api/file_stats") as ws:
        await ws.send('{"type":"file_stats","data":{"file_id":"' + file_id + '"}}')
        message = await asyncio.wait_for(ws.recv(), 60)
        message = loads(message)
        views = int(message['file_stats']['views'])
        return views

async def getPixelFileData(file_id:str):
    class FileData: pass
    async with aiohttp.ClientSession() as s:
        async with s.get('https://pixeldrain.com/u/' + file_id) as r:
            html = await r.text()
            vdata = re.findall(r'viewer_data[| ]=[| ](.*?);\n', html, re.DOTALL)
            if not vdata:
                # print(f'This Pixel File ({file_id}) cannot be fetched. Resp: {html}', flush=True)
                # open(f'test/{file_id}_{random.randint(100000, 999999)}.html', 'w', encoding='UTF-8').write(html)
                return file_id, None
            vdata = json.loads(vdata[0])
            for k, v in vdata['api_response'].items():
                setattr(FileData, k, v)
            try:
                FileData.views = await getViewsOfPixelFile(file_id)
            except:
                pass
            return file_id, FileData


async def getAllFileData(file_ids : list[str]):
    fids = file_ids.copy()
    fdatas = {}
    att = 0
    while fids:
        for task in asyncio.as_completed([getPixelFileData(fid_x) for fid_x in fids]):
            fid, fdata = await task
            fdatas[fid] = fdata
            if fdata: fids.remove(fid)
        att += 1
        if att > 70: break
        if fids: await asyncio.sleep(random.randint(5, 20))
    return fdatas


if __name__ == '__main__':
    fds = asyncio.run(getAllFileData(['6jYACerJ', '1V4j8Hmu']))
    # print(fds)
    for i, fd in fds.items():
        print(i, fd.availability)


