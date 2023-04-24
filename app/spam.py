import random

import dotenv

from models.base import session
from models.model import *

dotenv.load_dotenv()

pkg_codes = list(session.query(Packages.code, Packages.status).all())

cnt = 0
for i in range(0, 5):
    for j in range(0, 2000):
        cnt += 1
        random_order = random.choice(pkg_codes)
        pkg_code = random_order[0]
        pkg_status = random_order[1]
        if pkg_status < i:
            session.query(Packages).filter(Packages.code == pkg_code).update({'status': i})
            print("Ready to update: PKG_ORDER:", pkg_code + ', PKG_STATUS:', i)
            session.commit()
            session.flush()

print(cnt, "CNT >>>")
