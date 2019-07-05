import json

test = '{ \
"deviceid":"10005bd4af", \
"apikey":"9221d9fa-0418-4f8d-873c-f3ff27a80be1", \
"accept":"post" \
}'

print(json.loads(test))