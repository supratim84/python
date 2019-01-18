#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains a list of rester APIs implemented in flask framework 
designed to manage data about sporting events to allowing user to place bets.
author: supratim.ghosh1@gmail.com
"""
from flask import Response, abort, request, jsonify
from sqlalchemy import func, desc
from datetime import datetime
import sys

# Application specific modules
from app.models import Sport, Event, Market, Selection
from app import createApplication, db

# Create the flask app 
myapp = createApplication()


@myapp.route('/api/match/<int:matchId>', methods=['GET'])
def getMatchById(matchId):
	"""	Given a valid match id, this api responds with the match data including
	metadata like sport, market and selections. 
	Example url: localhost:5000/api/match/1

	@param int matchId: Match id number.
	@return json: json object containing match information.
	"""
	event = Event.query.filter_by(id=matchId).first_or_404()
	# We want to populate all the relationship data, hence the =False
	myapp.logger.info('Retrieving data for event %s', event.name)
	response = event.asDict(skipRelations=False)
	response.update({'url': request.url})
	return jsonify(response)


@myapp.route('/api/match/', methods=['GET'])
def getMatchesByName():
	"""Given a valid match name, this api responds with a list of match 
	information matching the name (contain basic basic information only).
	Example url: http://localhost:5000/api/match/?name=Real Madrid vs Barcelona

	@return json: List of dicts each contain match related information.
	"""
	response = []
	name = request.args.get('name')
	myapp.logger.info('Data requested for match %s', name)
	events = Event.query.filter_by(name=name)

	# For invalid name this api just returns an empty list does not raise and abort
	for event in events.order_by(desc('startTime')):
		res = event.asDict()
		res.update({'url': request.base_url + str(event.id)})
		response.append(res)

	return jsonify(matches=response)


@myapp.route('/api/match/<string:sportName>', methods=['GET'])
def getMatchesBySport(sportName):
	"""Given a valid sport name, this api returns a list of events related to 
	the sport, also takes an optional ordering parameter which by default 
	orders by event name in asc, startTime (if selection) in descending order.
	Example url: http://localhost:5000/api/match/football?ordering=startTime

	@param str sportName: Name of the sport like Football.
	@return list: Ordered list of matches for the selected sport.
	"""
	response = []
	# Check if the sport name is valid
	sport = Sport.query.filter(func.lower(Sport.name) == func.lower(sportName)).first_or_404()
		
	# Raise if requested ordering column is not valid
	orderBy = request.args.get('ordering')
	if orderBy and not getattr(Event, orderBy):
		myapp.logger.error('Column %s is not valid', orderBy)
		abort(404)

	# Only set desc order for startTime and set default ordering colum as name
	orderBy = orderBy or 'name'
	orderBy = desc(orderBy) if orderBy == 'startTime' else orderBy

	events = Event.query.filter_by(sportId=sport.id)
	for event in events.order_by(orderBy):
		myapp.logger.info('Event found: %s', event.name)
		res = event.asDict()
		res.update({'url': request.base_url.replace(sportName, str(event.id))})
		response.append(res)

	return jsonify(matches=response)


@myapp.route('/api/match/', methods=['POST'])
def messageHandler():
	"""Each message is expected to contain the full data for that event (match)
	Message types handled by this API are as below:
	 - NewEvent: A complete new sporting event is being created.
	 - UpdateOdds: There is an update for the odds field (all the other fields 
	remain unchanged)
	Url for POST: http://localhost:5000/api/match/

	@return Response: Appropriate response object with data as appropriate
	"""
	content = request.json
	messageType = content['message_type']
	event = content['event']
	# We assume there is only one market i.e. Winning, hence the [0]
	market = event['markets'][0]

	# Block that handles creation of a new match record (asumes a valid sport
	# is available and supplied in this event data)
	if messageType == 'NewEvent':
		# Check if sport id is valid
		sport = Sport.query.filter_by(id=event['sport']['id']).first_or_404()
		newEvent = Event(
			name=event['name'],
			startTime=datetime.strptime(
				event['startTime'], 
				'%Y-%m-%d %H:%M:%S'
			),
			sport=sport
		)
		
		# Create the market, assuming an instance of market is unique to an event
		newMarket = Market(name=market['name'], event=newEvent)
		
		# Create the initial set of selections w/o restricting collection length
		for selection in market['selections']:
			newSelection = Selection(
				name=selection['name'], 
				odds=selection['odds'], 
				market=newMarket
			)
			db.session.add(newSelection)
		
		db.session.commit()
		myapp.logger.info('New event %s created', newEvent.name)
		return Response('Event created', 201)
	
	
	# Block that handles update odds (only) request, ensures no other fields are updated 
	elif messageType == 'UpdateOdds':
		# Check if event id is valid
		selEvent = Event.query.filter_by(id=event['id']).first_or_404()
		myapp.logger.info('Selected event is %s', selEvent.name)

		# Now that we know event is valid, we find the  market and retrieve its selections
		selMarket = Market.query.filter_by(eventId=selEvent.id).first_or_404()
		newOddsMap = dict((sel['id'], sel['odds']) for sel in market['selections'])

		for selection in selMarket.selections:
			newOdds = newOddsMap.get(selection.id)
			# Check if None to get 0.0 pass in as valid
			if newOdds is not None and newOdds != selection.odds:
				selection.odds = newOdds
				myapp.logger.info(
					'Selection %s updated with odds %f', 
					selection.name, 
					selection.odds
				)

		db.session.commit()
		return Response('', 204)
		
	myapp.logger.error('Message type %s is not valid', messageType)
	return Response('Bad request', 400)


if __name__ == '__main__':
	myapp.run(use_reloader=True)
