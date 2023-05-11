from models.base import session
import random

from models.model import Packages

for i in range(1, 1000000):
    shop_id = random.choice(range(1, 4))
    current_station_id = random.choice(range(1, 6))
    customer_id = random.choice(range(1, 7))
    package = {}
    order = str(i).zfill(6)
    print(order)
    packages = Packages(id=i, shop_id=shop_id, current_station_id=current_station_id,
                        customer_id=customer_id, status=0, code='P' + order)
    session.add(packages)
    session.commit()
