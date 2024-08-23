from helper import getLinkRows, updateLinkRows, time

rows = getLinkRows(0)[:1]

for row in rows:
    row['last_visit'] = int(time.time() / 60 - 2*24*60)

updateLinkRows(rows)
