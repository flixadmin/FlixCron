from seleniumwire import webdriver
from tempfile import NamedTemporaryFile
import time, random

def open_in_parallel(file_ids:list, proxy:str=None):
    with NamedTemporaryFile(suffix='.html', delete=False) as f:
        f.write(''.join([f'<iframe src="https://pixeldrain.com/u/{i}?embed"></iframe>' for i in file_ids]).encode())
        file_uri = f.name
        f.close()
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options, seleniumwire_options={'proxy': dict(http=proxy, https=proxy)})
    driver.get(file_uri)
    # driver.get(f'http://ip.oxylabs.io?id={random.randint(1000, 9999)}')
    # for pr in proxies:
        # print(pr)
        # driver.proxy = dict(http=pr, https=pr)
        # time.sleep(10)
        # driver.get(f'http://ip.oxylabs.io?id={random.randint(1000, 9999)}')
    time.sleep(10)
    driver.quit()

if __name__ == '__main__':
    import free_proxies
    for pr in free_proxies.working_proxies():
        try:
            open_in_parallel(['1V4j8Hmu'], pr)
        except: pass
    