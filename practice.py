from helper import getLinkRows, getAllFileData
import asyncio, random

rows = getLinkRows(0)

file_ids = [row['url'].split('/u/')[1].split('/')[0].split('?')[0] for row in rows]
random.shuffle(file_ids)
print(len(file_ids))
# for i in range(30):
    # asyncio.run(getAllFileData(file_ids), debug=False)

