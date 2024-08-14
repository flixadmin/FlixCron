from helper import getLinkRows, updateLinkRows
import time

rows = getLinkRows(0)

for r in rows:
    r['last_visit'] = int(time.time() / 60 - 10 * 24 * 60) # minus 10 days

updateLinkRows(rows)