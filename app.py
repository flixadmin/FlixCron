from flask import Flask, redirect
import os, time, random


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


if __name__ == '__main__':
    app.run(port=8080, debug=True)
