import random

import dotenv

from models.base import session
from sqlalchemy import update
from models.model import *

dotenv.load_dotenv()

pkg_orders = ['P102', 'P664', 'P503', 'P208', 'P952', 'P231', 'P751', 'P152']

for i in range(0, 5):
    for j in range(1, 8):
        random_order = random.choice(pkg_orders)
        print("Ready to update: PKG_ORDER:", random_order, ', PKG_STATUS:', i)
        session.query(Packages).filter(Packages.pkg_order == random_order).update({'status': i})
        session.commit()
        session.flush()
