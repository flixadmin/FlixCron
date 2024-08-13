from pixel_view import run_all_with_proxies, run_with_proxies
from helper import *
import logging, sys


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.propagate = False
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s]: %(message)s', '%d/%m/%y %H:%M:%S UTC+0')
formatter.converter = time.gmtime
handler.setFormatter(formatter)
log.addHandler(handler)


log.info('Fetching Links...')
rows = getLinkRows(1)
log.info(f'Fetched {len(rows)} links.')

if len(rows) == 0:
    log.info(f'Exitting since no links fetched.')
    sys.exit()

file_ids = [row['url'].split('/u/')[1].split('/')[0].split('?')[0] for row in rows]

log.info('Fetching all files...')
old_link_states = asyncio.run(getAllFileData(file_ids))
log.info('Fetched all files info.')

# old_time = time.time()
# while time.time() < old_time + 30 * 60: # 30 mins
#     log.info('Sending views to all files')
#     from free_proxies import all_proxies
#     asyncio.run(run_all_with_proxies(file_ids, all_proxies))
#     log.info('Attempt Successfully Completed.')

for fid in file_ids:
    log.info(f'Sending views to {fid}')
    from free_proxies import all_proxies
    asyncio.run(run_with_proxies(fid, all_proxies))
    log.info('Completed.')

log.info('Fetching all files again...')
new_link_states = asyncio.run(getAllFileData(file_ids))
log.info('Fetched all files info.')

log.info('Analysing...')
views_sent = {}
for fid in file_ids:
    ols = old_link_states.get(fid)
    nls = new_link_states.get(fid)
    if ols and nls:
        views_sent[fid] = nls.views - ols.views
    else:
        views_sent[fid] = None

for k, v in views_sent.items():
    if v: log.info(f'File -> {k} got {v} views')
    else: log.error(f'Something went wrong with file -> {k}')

for fid, fd in new_link_states.items():
    if fd and days_from_now(fd.date_last_view) > 60:
        log.error(f'Alas! This file -> {fid} gonna expire soon. Manually visit needed.')
    if fd and fd.availability != '':
        log.error(f'Hotlink Protection Found. Reupload or Grab needed.')

log.info('Updating links database...')
cur_time = int(time.time() / 60)
for row in rows:
    row['last_visit'] = cur_time

updateLinkRows(rows)
log.info('Database Updated.')
log.info('Task Completed!')

