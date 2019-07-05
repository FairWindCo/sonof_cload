import argparse
import json
import os
import sys
from time import sleep

import requests

from non_block_key import KBHit
from wifi.wifi import WiFiUtils

wifi = WiFiUtils()
kb = KBHit()
count = 0

print('Hit ESC to exit')

chars = ['-', '\\', '|', '/']

config = {
    "router": {
        "SSID": "##########",
        "password": "###########"
    },
    "server": {
        "ip": "192.168.0.1",
        "httpPort": 1080,
        "httpsPort": 1081,
        "websocketPort": 1443
    }
}

parser = argparse.ArgumentParser(description='Configure utils.')
parser.add_argument('--ssid', action="store", type=str)
parser.add_argument('--passwd', action="store", type=str)
parser.add_argument('--ip', action="store", type=str)
parser.add_argument('--http', action="store", type=str)
parser.add_argument('--https', action="store", type=str)
parser.add_argument('--sock', action="store", type=str)

args = parser.parse_args()


if args.ssid:
    config['router']['SSID'] = args.ssid
if args.passwd:
    config['router']['password'] = args.passwd
if args.ip:
    config['server']['ip'] = args.ip
if args.http:
    config['server']['httpPort'] = args.http
if args.https:
    config['server']['httpsPort'] = args.https
if args.sock:
    config['server']['websocketPort'] = args.sock

print(config)

while True:
    if kb.kbhit():
        c = kb.getch()
        if ord(c) == 27:  # ESC
            break
    sids = wifi.get_wifi_list()

    for sid in sids:
        if 'ITEAD-10' in sid:
            print('\n')
            print('found sid: ' + sid)
            wifi.connect(sid, '12345678', True)
            res = requests.get('http://10.10.7.1/device')
            if res.status_code == 200:
                dev = json.loads(res.text)
                print('Found Device : '+dev['deviceid'])
                config = {
                    "version": 4,
                    "ssid": config['router']['SSID'],
                    "password": config['router']['password'],
                    "serverName": config['server']['ip'],
                    "port": config['server']['httpsPort']
                }
                res = requests.post('http://10.10.7.1/ap',json=config)
                if res.status_code == 200:
                    print('Device Answer: ' + res.text)
                    print('DEVICE CONFIGURED!')
                else:
                    print('ERROR CONFIGURATION!')
                os._exit(0)
                break

    #wifi.connect('Cisco_24', 'nkt12345', True)
    sys.stdout.write("Wait for Sonoff wifi ap - %s%%   \r" % (chars[count % 4]))
    sys.stdout.flush()
    count += 1
    sleep(0.1)

kb.set_normal_term()