import random

import dotenv

from models.model import *

dotenv.load_dotenv()

pkg_orders = ['P102', 'P664', 'P503', 'P208', 'P952', 'P231', 'P751', 'P152']

for i in range(0, 5):
    for j in range(1, 8):
        Packages.update({Packages.status: i}).where(Packages.pkg_order == random.choice(pkg_orders)).execute()