from DrissionPage import ChromiumPage, ChromiumOptions
from time import sleep

def visitPages(urls:list[str]):
  opts = ChromiumOptions()
  opts.auto_port(True)
  opts.set_argument('--start-maximized')
  page = ChromiumPage(opts)

  for url in urls:
    page.get(url)
    sleep(10)
  page.quit()

