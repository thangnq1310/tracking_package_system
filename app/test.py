import ujson as json

import redis

s = {
    'shop_id': 1,
    'webhook_url': '/api/list',
    'response_time': [1, 2.5, 3.1],
    "avg_time": 9.1
}

cache = redis.Redis(
            host='localhost',
            port=6379
)

cache.set(s['shop_id'], json.dumps(s))

res = json.loads(cache.get("1"))

print(res)