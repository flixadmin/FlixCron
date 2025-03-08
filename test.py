from helper import *
import asyncio

d = asyncio.run(getAllFileData(['eukLgo9i', 'Ss4P1dxN', 'mEqF7TvC', 'rwpAXm1c', '2pSrNHAk', 'bKyqyTDx',
                'KH23j6X3', 'DQcQcci7', 'H4Duk1bR', 'Pj1heDFe', 'Ev7VjqtK', 'yD71HmCm', 'emxNpP9F', 'fAh4Gpir', 'ZxDgxpPv']))

for i, f in d.items():
  print(i, ':', f.date_last_view)

