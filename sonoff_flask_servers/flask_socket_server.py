from datetime import datetime
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send

app = Flask(__name__)

#app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

clients = []
devices = {}

@app.route('/')
def index():
    print('received message: ', request.endpoint)
    return 'OK'


@socketio.on('connected')
def connected():
    print("%s connected" % (request.namespace.socket.sessid))
    clients.append(request.namespace)


@socketio.on('disconnect')
def disconnect():
    print("%s disconnected" % (request.namespace.socket.sessid))
    clients.remove(request.namespace)

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)


@socketio.on('json')
def handle_json(json):
    if 'deviceid' not in  json:
        send({'error':1}, json=True)
        return

    deviceid = json['deviceid']
    res = {
        "error": 0,
        "deviceid": deviceid,
        "apikey": "111111111-1111-1111-1111-111111111111"
    };


    print('received json: ' + str(json))

    if json['action'] == 'date':
        res['date']=datetime.datetime.now().isoformat()
    elif json['action'] == 'query':
        if deviceid in devices:
            device = devices[deviceid]
            res['params'] = device['params']
        else:
            print('Unknown device id' + deviceid)
    elif json['action'] == 'update':
        if deviceid in devices:
            device = devices[deviceid]
            device['updated'] = datetime()
            device['state'] = json['params']
        else:
            print('Unknown device id'+deviceid)
    elif json['action'] == 'register':
        dev_type = deviceid[:2]
        if dev_type == '01':
            dev_kind = 'switch'
        elif dev_type == '02':
            dev_kind = 'light'
        elif dev_type == '03':
            dev_kind = 'sensor'
        else:
            dev_kind = 'other'
        version = json['romVersion']
        model = json['model']

        device = {
            'deviceid' : deviceid,
            'dev_type': dev_type,
            'dev_kind': dev_kind,
            'version': version,
            'model':model,
            'state': json['params'] if 'params' in json else None,
            'register': datetime(),
            'updated': datetime()
        }

        devices[deviceid] = device
        print('register device:' + device)
    else:
        print('TODO | Unknown action' + json['action'] )

    send(res, json=True)



#if __name__ == '__main__':
#    app.run()
if __name__ == '__main__':
     print("run websocket server")
     context = ('server.crt', 'server.key')  # certificate and key files
     socketio.run(app, host='0.0.0.0', port=1443, debug=True, keyfile='server.key', certfile='server.crt', ssl_version=2)

