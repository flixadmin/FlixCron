from helper import getLinkRows, getAllFileData, updateLinkRows, time
import asyncio, random

rows = getLinkRows(0)[:10]

for row in rows:
    row['last_visit'] = int(time.time() / 60 - 2*24*60)

updateLinkRows(rows)

# file_ids = [row['url'].split('/u/')[1].split('/')[0].split('?')[0] for row in rows]
# random.shuffle(file_ids)
# print(len(file_ids))

# for i in range(30):
#     data = asyncio.run(getAllFileData(file_ids))
#     for fid, fd in data.items():
#         if not fd:
#             print(f'Error in file {fid}')

