from models.base import session
import random

from models.model import Packages

for i in range(1, 10001):
    shop_id = random.choice(range(1, 4))
    current_station_id = random.choice(range(1, 6))
    customer_id = random.choice(range(1, 7))
    package = {}
    packages = Packages(id=i, shop_id=shop_id, current_station_id=current_station_id, customer_id=customer_id, status=0, pkg_order='P' + str(i))
    session.add(packages)
    session.commit()