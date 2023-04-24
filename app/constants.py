PKG_STATUS = {
    'IS_TRANSFERRING': 0,
    'PENDING_SHIP': 1,
    'IS_SHIPPING': 2,
    'SHIPPED': 3,
    'CANCELED': 4
}

# RANK_TOPIC = {
#     'platinum': 'platinum_topic',
#     'gold': 'gold_topic',
#     'silver': 'silver_topic'
# }

RANK_TOPIC = ['connector.logistic.packages', 'gold_topic', 'silver_topic']

LIMIT_MSG = 50
LIMIT_REDIS_MSG = 100
TIMEOUT_MSG = 5000
PLATINUM_TIMEOUT_REQUEST = 0.4
GOLD_TIMEOUT_REQUEST = 0.6
SILVER_TIMEOUT_REQUEST = 1
STATUS_ALLOW = [429, 404, 500, 502, 503, 504]
