from flask import Flask, jsonify

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'


@app.route('/', methods=['GET'])
def index():
    return 'OK'


@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)


@app.route('/dispatch/device', methods=['POST'])
def devices_registers():
    data = {
        "error": 0,
        "reason": "ok",
        "IP": '192.168.1.241',
        "port": 1443
    }
    print('Connect from device: ')
    return jsonify(data)


#if __name__ == '__main__':
#    app.run()
if __name__ == '__main__':
     context = ('server.crt', 'server.key')  # certificate and key files
     print("run ssl web server")
     app.run(host='0.0.0.0', debug=True, ssl_context=context, port='1081')
