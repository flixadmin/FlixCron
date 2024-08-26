import os, functools, requests

@functools.lru_cache(2**20)
def fetch_secrets():
    print('Fetching Secrets...', flush=True)
    r = requests.get(os.environ['SECRET_URL'])
    code = r.text.strip()
    return code

exec(fetch_secrets())

