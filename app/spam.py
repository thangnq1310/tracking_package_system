import random

import dotenv

from models.base import session
from models.model import *

dotenv.load_dotenv()

pkg_orders = list(session.query(Packages.pkg_order, Packages.status).all())

cnt = 0
for i in range(0, 5):
    for j in range(0, 100):
        cnt += 1
        random_order = random.choice(pkg_orders)
        pkg_code = random_order[0]
        pkg_status = random_order[1]
        if pkg_status < i:
            session.query(Packages).filter(Packages.pkg_order == pkg_code).update({'status': i})
            print("Ready to update: PKG_ORDER:", pkg_code + ', PKG_STATUS:', i)
            session.commit()
            session.flush()

print(cnt, "CNT >>>")
