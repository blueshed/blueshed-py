from blueshed.model_helpers.base import Base
from sqlalchemy.types import String, Integer, Numeric, DateTime, Date, Time, Enum, Boolean, Text
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative.api import declared_attr, has_inherited_table, declarative_base
import re


customer_addresses_address = Table('customer_addresses_address', Base.metadata,
    Column('addresses_id', Integer, ForeignKey('customer.id')),
    Column('address_id', Integer, ForeignKey('address.id')),
    mysql_comment='{\"back_ref\":\"Customer.addresses\", \"back_populates\":\"Address.customers\"}',
    mysql_engine='InnoDB')


class Address(Base):
    
    id = Column(Integer, primary_key=True)
    line1 = Column(String(100))
    line2 = Column(String(80))
    town = Column(String(80))
    postcode = Column(String(10))
    county = Column(String(80))
    customers = relationship('Customer',
        secondaryjoin='Customer.id==customer_addresses_address.c.addresses_id',
        primaryjoin='Address.id==customer_addresses_address.c.address_id',
        secondary='customer_addresses_address',
        lazy='joined', back_populates='addresses')
    delivery_customers = relationship('Customer', uselist=True, 
        primaryjoin='Customer.delivery_address_id==Address.id',
        remote_side='Customer.delivery_address_id',
        back_populates='delivery_address')


class Customer(Base):
    
    CUSTOMER_TYPE = ['retail','wholesale']
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    dob = Column(Date)
    active = Column(Boolean())
    customer_type = Column(Enum(*CUSTOMER_TYPE))
    addresses = relationship('Address',
        primaryjoin='Customer.id==customer_addresses_address.c.addresses_id',
        secondaryjoin='Address.id==customer_addresses_address.c.address_id',
        secondary='customer_addresses_address',
        lazy='joined', back_populates='customers')
    delivery_address_id = Column(Integer, ForeignKey('address.id'))
    delivery_address = relationship('Address', uselist=False,
        primaryjoin='Customer.delivery_address_id==Address.id', 
        remote_side='Address.id',
        back_populates='delivery_customers')


class Note(Base):
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    author = Column(String(255))
    items = relationship('NoteItem', uselist=True, 
        primaryjoin='NoteItem.note_id==Note.id',
        remote_side='NoteItem.note_id',
        back_populates='note')


class NoteItem(Base):
    
    TYPE = ['note','image','map']
    
    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey('note.id'))
    note = relationship('Note', uselist=False,
        primaryjoin='NoteItem.note_id==Note.id', 
        remote_side='Note.id',
        back_populates='items')
    text = Column(Text)
    image = Column(String(255))
    lat = Column(Numeric(12,8))
    lng = Column(Numeric(12,8))
    zoom = Column(Integer)
    map_type = Column(String(80))
    row = Column(Integer)
    col = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    type = Column(Enum(*TYPE))
    