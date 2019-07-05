from sonoff import sonoff

s = sonoff.Sonoff('sergey.manenok@gmail.com', 'q1s2c3f4t5', 'eu')
devices = s.get_devices()

for device in devices:
    # We found a device, lets turn something on
    device_id = device['deviceid']
    for key,val in devices[0].items():
        print(key, val)
    s.switch('on', device_id, 0)
    s.switch('off', device_id, 0)



