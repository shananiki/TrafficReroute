import time
from threading import Thread

from flask import Flask, request, send_file, jsonify
import webbrowser
import handlers, events, proxy


app = Flask(__name__)

@app.route('/')
def index():
    return send_file('templates/index.html')


@app.route('/api/v1/throttle/client-server', methods=['POST'])
def throttle_client_server():
    duration = int(request.form.get('duration'))
    handler = handlers.throttle_client_server(duration)
    events.add(handler, target='client')
    return jsonify({'success': True})


if __name__ == '__main__':
    Thread(target=proxy.run).start()
    Thread(target=lambda: time.sleep(2) or webbrowser.open('http://localhost:5000')).start()
    app.run()
