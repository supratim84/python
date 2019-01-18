#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains the application's data models. SQLAlchemy used to define relations
between various models and sqlite to facilitate storage.
author: supratim.ghosh1@gmail.com
"""
from app import db


class Sport(db.Model):
	"""Representation of the sports table, has a one to many relationship with Events.
	when Events are populated sport.events will render the list of events mapped to
	a unique of a sport whose name is considered unique
	"""
	__tablename__ = 'sport'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), index=True, unique=True)

	def asDict(self):
		return dict(id=self.id, name=self.name)

	def __repr__(self):
		return '<%s>%s' % (self.__class__.__name__, self.name)


class Event(db.Model):
	"""Representation of the events/matches table, has a many to one relation
	with the sport table.
	"""
	__tablename__ = 'event'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(250), index=True)
	startTime = db.Column(db.DateTime)
	sportId = db.Column(db.Integer, db.ForeignKey('sport.id'))
	sport = db.relationship(Sport, backref=db.backref('events', uselist=True))

	def asDict(self, skipRelations=True):
		"""Returns a dictionary with event data

		:param bool skipRelations: when set to true only return even information and not
		related to the mapped sport or market
		:return dict: dictionary with event information
		"""
		eventDict = dict(id=self.id, name=self.name, startTime=str(self.startTime))
		if not skipRelations:
			eventDict.update(
				dict(
					sport=self.sport.asDict(),
					markets=map(lambda m:m.asDict(), self.markets),
				)
			)
		return eventDict

	def __repr__(self):
		return '<%s>%s>%s' % (
			self.__class__.__name__,
			self.sport.name,
			self.name
		)


class Market(db.Model):
	"""Representation of the market table.
	Has a many to one relationship with event and is deemed to be unique per sport. 
	"""
	__tablename__ = 'market'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), index=True)
	eventId = db.Column(db.Integer, db.ForeignKey('event.id'))
	event = db.relationship(Event, backref=db.backref('markets', uselist=True))

	def asDict(self):
		return dict(
			id=self.id,
			name=self.name,
			selections=map(lambda s:s.asDict(), self.selections)
		)

	def __repr__(self):
		return '<%s>%s>%s>%s' % (
			self.__class__.__name__,
			self.event.sport.name,
			self.event.name,
			self.name
		)


class Selection(db.Model):
	"""Representation of the selections table.
	Has a many to one relation with market and this collection is unique per market.
	"""
	__tablename__ = 'selection'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), index=True)
	odds = db.Column(db.Float)
	marketId = db.Column(db.Integer, db.ForeignKey('market.id'))
	market = db.relationship(Market, backref=db.backref('selections', uselist=True))
	
	def asDict(self):
		return dict(id=self.id, name=self.name, odds=self.odds)

	def __repr__(self):
		return '<%s>%s>%s>%s>%s' % (
			self.__class__.__name__,
			self.market.event.sport.name,
			self.market.event.name,
			self.market.name,
			self.name
		)
