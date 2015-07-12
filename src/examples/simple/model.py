from blueshed.model_helpers.base import Base
from sqlalchemy.types import String, Integer, Numeric, DateTime, Date, Time, Enum, Boolean, Text
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative.api import declared_attr, has_inherited_table, declarative_base
import re


service_grant_steps_step = Table('service_grant_steps_step', Base.metadata,
	Column('grant_steps_id', Integer, ForeignKey('service.id')),
	Column('step_id', Integer, ForeignKey('step.id')),
	mysql_engine='InnoDB')


service_revoke_steps_step = Table('service_revoke_steps_step', Base.metadata,
	Column('revoke_steps_id', Integer, ForeignKey('service.id')),
	Column('step_id', Integer, ForeignKey('step.id')),
	mysql_engine='InnoDB')


user_requirements_service = Table('user_requirements_service', Base.metadata,
	Column('requirements_id', Integer, ForeignKey('user.id')),
	Column('service_id', Integer, ForeignKey('service.id')),
	mysql_engine='InnoDB')


user_fullfilments_step = Table('user_fullfilments_step', Base.metadata,
	Column('fullfilments_id', Integer, ForeignKey('user.id')),
	Column('step_id', Integer, ForeignKey('step.id')),
	mysql_engine='InnoDB')


class History(Base):
	
	ACTION = ['added','removed']
	
	id = Column(Integer, primary_key=True)
	person_id = Column(Integer, ForeignKey('user.id'))
	person = relationship('User', uselist=False,
		primaryjoin='History.person_id==User.id', remote_side='User.id',
		back_populates='history')
	step_id = Column(Integer, ForeignKey('step.id'))
	step = relationship('Step', uselist=False,
		primaryjoin='History.step_id==Step.id', remote_side='Step.id',
		back_populates='history')
	service_id = Column(Integer, ForeignKey('service.id'))
	service = relationship('Service', uselist=False,
		primaryjoin='History.service_id==Service.id', remote_side='Service.id',
		back_populates='history')
	action = Column(Enum(*ACTION))
	created = Column(DateTime)


class Service(Base):
	
	id = Column(Integer, primary_key=True)
	name = Column(String(255))
	system_id = Column(Integer, ForeignKey('system.id'))
	system = relationship('System', uselist=False,
		primaryjoin='Service.system_id==System.id', remote_side='System.id',
		back_populates='services')
	grant_steps = relationship('Step',
		primaryjoin='Service.id==service_grant_steps_step.c.grant_steps_id',
		secondaryjoin='Step.id==service_grant_steps_step.c.step_id',
		secondary='service_grant_steps_step',
		lazy='joined', back_populates='grant_services')
	revoke_steps = relationship('Step',
		primaryjoin='Service.id==service_revoke_steps_step.c.revoke_steps_id',
		secondaryjoin='Step.id==service_revoke_steps_step.c.step_id',
		secondary='service_revoke_steps_step',
		lazy='joined', back_populates='revoke_services')
	history = relationship('History', uselist=True, 
		primaryjoin='History.service_id==Service.id', remote_side='History.service_id',
		back_populates='service')
	people = relationship('User',
		secondaryjoin='User.id==user_requirements_service.c.requirements_id',
		primaryjoin='Service.id==user_requirements_service.c.service_id',
		secondary='user_requirements_service',
		lazy='joined', back_populates='requirements')


class Step(Base):
	
	id = Column(Integer, primary_key=True)
	name = Column(String(255))
	prerequisit_id = Column(Integer, ForeignKey('step.id'))
	prerequisit = relationship('Step', uselist=False,
		primaryjoin='Step.prerequisit_id==Step.id', remote_side='Step.id')
	history = relationship('History', uselist=True, 
		primaryjoin='History.step_id==Step.id', remote_side='History.step_id',
		back_populates='step')
	grant_services = relationship('Service',
		secondaryjoin='Service.id==service_grant_steps_step.c.grant_steps_id',
		primaryjoin='Step.id==service_grant_steps_step.c.step_id',
		secondary='service_grant_steps_step',
		lazy='joined', back_populates='grant_steps')
	revoke_services = relationship('Service',
		secondaryjoin='Service.id==service_revoke_steps_step.c.revoke_steps_id',
		primaryjoin='Step.id==service_revoke_steps_step.c.step_id',
		secondary='service_revoke_steps_step',
		lazy='joined', back_populates='revoke_steps')
	people = relationship('User',
		secondaryjoin='User.id==user_fullfilments_step.c.fullfilments_id',
		primaryjoin='Step.id==user_fullfilments_step.c.step_id',
		secondary='user_fullfilments_step',
		lazy='joined', back_populates='fullfilments')


class System(Base):
	
	id = Column(Integer, primary_key=True)
	name = Column(String(255))
	services = relationship('Service', uselist=True, 
		primaryjoin='Service.system_id==System.id', remote_side='Service.system_id',
		back_populates='system')


class User(Base):
	
	id = Column(Integer, primary_key=True)
	email = Column(String(128))
	_password = Column(String(80))
	name = Column(String(255))
	requirements = relationship('Service',
		primaryjoin='User.id==user_requirements_service.c.requirements_id',
		secondaryjoin='Service.id==user_requirements_service.c.service_id',
		secondary='user_requirements_service',
		lazy='joined', back_populates='people')
	fullfilments = relationship('Step',
		primaryjoin='User.id==user_fullfilments_step.c.fullfilments_id',
		secondaryjoin='Step.id==user_fullfilments_step.c.step_id',
		secondary='user_fullfilments_step',
		lazy='joined', back_populates='people')
	history = relationship('History', uselist=True, 
		primaryjoin='History.person_id==User.id', remote_side='History.person_id',
		back_populates='person')

