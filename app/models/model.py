"""SQLAlchemy Data Models."""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String


Base = declarative_base()


class Packages(Base):
    """Packages."""

    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    shop_id = Column(Integer, ForeignKey('shops.id'))
    current_station_id = Column(Integer, ForeignKey('stations.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    status = Column(Integer)
    pkg_order = Column(String(6), unique=True, nullable=False)


class Shops(Base):
    """Shops."""

    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    name = Column(String(150))
    email = Column(String(100))
    webhook_url = Column(String(100))
    packages = relationship('Packages')


class Customers(Base):
    """Customers."""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    name = Column(String(150))
    email = Column(String(100))
    address_id = Column(Integer, ForeignKey('addresses.id'))
    packages = relationship('Packages')


class Stations(Base):
    """Stations."""

    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    name = Column(String(150))
    address_id = Column(Integer, ForeignKey('addresses.id'))
    packages = relationship('Packages')


class Addresses(Base):
    """Addresses."""

    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    name = Column(String(150))
    customers = relationship('Customers')
    stations = relationship('Stations')

