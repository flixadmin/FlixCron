from helper import getPixelFileData
import asyncio

d = asyncio.run(getPixelFileData('o3xpCTPw'))

print(d[1].date_last_view)

