from pixel_view import run_all_with_proxies, run_with_proxies
from helper import *
import logging, sys, asyncio

import nest_asyncio
nest_asyncio.apply()

exec(os.environ.get('ENC_IT', 'enc_it = lambda x: x'))
enc_it = globals()['enc_it']

logging.getLogger('asyncio').disabled = True
# logging.getLogger('asyncio').setLevel(logging.CRITICAL)
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

log.info('Updating links database temporary...')
max_cron_run_hour = 3
for row in rows:
    row['last_visit'] = int(row['last_visit']) + max_cron_run_hour * 60

updateLinkRows(rows)
log.info('Database Updated.')

file_urls = [row['url'] for row in rows]
file_ids = [row['url'].split('/u/')[1].split('/')[0].split('?')[0] for row in rows]
random.shuffle(file_ids)

log.info('Fetching all files...')
old_link_states = asyncio.run(getAllFileData(file_ids))
log.info('Fetched all files info.')
"""
for fid in file_ids:
    log.info(f'Sending views to {enc_it(fid)}')
    from free_proxies import all_proxies
    asyncio.run(run_with_proxies(fid, [*all_proxies, None]))
    log.info('Completed.')
"""
log.info('Sending Views to all files...')
endpoint = os.environ['PD_ENDPOINT']
if not endpoint:
    raise Exception('Please set the PD_ENDPOINT environment variable')
for i in range(random.randint(150, 500)):
    r = requests.post(endpoint, json=file_urls)
    if r.status_code!=200:
        log.info(f'Error in the server: Status code - {r.status_code}')
    time.sleep(random.randint(3, 10))
log.info('Completed!')

log.info('Checking for hotlinked files')
hfiles = ['https://pixeldrain.com/u/' + fid for fid, fd in old_link_states.items() if fd.availability!='']
required_views = [fd.downloads - fd.views for fid, fd in old_link_states.items() if fd.availability!='']
required_views.sort()
needed_view = next(iter(required_views), 0)
log.info(f'Found {len(hfiles)} hotlinked files')
if len(hfiles)!=0:
    log.info(f'Sending views to hotlinked files')
    for i in range(needed_view):
        r = requests.post(endpoint, json=hfiles)
        if r.status_code != 200:
            log.info(f'Error in the server: Status code - {r.status_code}')
        time.sleep(random.randint(3, 10))
    log.info('Completed!')
# """
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
        log.error(f'The file -> {enc_it(fid)} cannot be fetched')
        views_sent[fid] = None

error_files = []
hotlinked_files = []
expiring_files = []

for k, v in views_sent.items():
    if not v is None: log.info(f'File -> {enc_it(k)} got {v} views')
    else:
        error_files.append('https://pixeldrain.com/u/' + k)
        log.error(f'Something went wrong with file -> {enc_it(k)}')

for fid, fd in new_link_states.items():
    if fd and days_from_now(fd.date_last_view) > 60:
        expiring_files.append('https://pixeldrain.com/u/' + fid)
        log.error(f'Alas! This file -> {enc_it(fid)} gonna expire soon. Manually visit needed.')
    if fd and fd.availability != '':
        hotlinked_files.append('https://pixeldrain.com/u/' + fid)
        log.error(f'Hotlink Protection Found for file -> {enc_it(fid)}. Reupload or Grab needed.')


log.info('Sending Emails if needed...')
if error_files: send_mail(f'FlixCron: Files that cannon be accessed ({random.randint(11111, 99999)})', '<br>'.join([f'{i+1}. {u}' for i, u in enumerate(error_files)]))
if expiring_files: send_mail(f'FlixCron: These files are gonna expire soon ({random.randint(11111, 99999)})', '<br>'.join([f'{i+1}. {u}' for i, u in enumerate(expiring_files)]))
if hotlinked_files: send_mail(f'FlixCron: Grab needed for these hotlinked files ({random.randint(11111, 99999)})', '<br>'.join([f'{i+1}. {u}' for i, u in enumerate(hotlinked_files)]))


log.info('Updating links database...')
cur_time = int(time.time() / 60)
max_delay = 3 # hours
for row in rows:
    row['last_visit'] = cur_time + random.randint(max_delay * -60, max_delay * 60)

updateLinkRows(rows)
log.info('Database Updated.')

log.info('Task Completed!')

