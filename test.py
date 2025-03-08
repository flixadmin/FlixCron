from helper import getPixelFileData
import asyncio

d = asyncio.run(getPixelFileData('rmJXJF2s'))

print(d[1].date_last_view)

