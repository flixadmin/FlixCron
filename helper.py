import psycopg2, os, time, aiohttp, re, json, asyncio, random, requests, traceback
from datetime import datetime, timezone


def days_from_now(time_str):
    return (datetime.now(timezone.utc) - datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)).days

def send_mail(subject:str, body:str):
    try:
        r = requests.post(os.environ['MAIL_URI'], data={'s': subject, 'b': body})
        if not r.json()['success']:
            raise Exception('Cannot send email. View server logs.')
    except:
        print(traceback.format_exc(), flush=True)

def getLinkRows(last_updated_day_ago : int = 0):
    before_time = int(time.time() / 60) - last_updated_day_ago * 24 * 60
    conn = psycopg2.connect(os.environ.get('FW_DB_URI'))
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
    conn = psycopg2.connect(os.environ.get('FW_DB_URI'))
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

async def getPixelFileData(file_id:str):
    class FileData: pass
    async with aiohttp.ClientSession() as s:
        async with s.get('https://pixeldrain.com/u/' + file_id) as r:
            html = await r.text()
            vdata = re.findall(r'viewer_data[| ]=[| ](.*?);', html, re.DOTALL)
            if not vdata: 
                print(f'This Pixel File ({file_id}) cannot be fetched', flush=True)
                return file_id, None
            vdata = json.loads(vdata[0])
            for k, v in vdata['api_response'].items():
                setattr(FileData, k, v)
            return file_id, FileData


async def getAllFileData(file_ids : list[str]):
    fids = file_ids.copy()
    fdatas = {}
    att = 0
    while fids:
        for task in asyncio.as_completed([getPixelFileData(fid) for fid in fids]):
            fid, fdata = await task
            fdatas[fid] = fdata
            if fdata: fids.remove(fid)
        att += 1
        if att > 7: return fdata
        await asyncio.sleep(random.randint(3, 7))
    return fdatas


if __name__ == '__main__':
    fds = asyncio.run(getAllFileData(['VMM2fgUy']))
    print(fds)


