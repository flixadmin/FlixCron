from flask import Flask, redirect
from requests import get
import os, time, random, threading

try: os.mkdir('static')
except FileExistsError: pass

def keep_alive():
    while 1:
        time.sleep(60)
        try: get('https://flixcron.onrender.com/')
        except: print('Cannot do keep alive request', flush=True)

def list_files_by_creation_time(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)), reverse=True)
    return files
 

app = Flask(__name__)

@app.route('/')
def index():
    files = list_files_by_creation_time('static')
    html = ''
    for file in files:
        html += f'<a href="/static/{file}">{file}</a><br>'
    return html

@app.route('/run')
def cron_run():
    log_file = f'log_{int(time.time())}_{random.randint(1000, 9999)}.txt'
    os.system(f'python main.py > static/{log_file} 2>&1')
    return redirect(f'/static/{log_file}')


t = threading.Thread(target=keep_alive)
t.daemon = True
t.start()

if __name__ == '__main__':
    app.run(port=8080, debug=True)
