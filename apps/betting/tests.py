#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""This module unit tests for the rester APIS in server.py
author: supratim.ghosh1@gmail.com
"""
from app.models import Sport, Event, Market, Selection
from app import db, getOrCreate
from server import myapp

from datetime import datetime
import unittest
import json


class TestBetApp(unittest.TestCase):
    def setUp(self):
    	self.app = myapp
        self.app.config.update(
            TESTING = True,
            SQLALCHEMY_ECHO = False,
            SQLALCHEMY_DATABASE_URI = 'sqlite://',
        )
    	self.client = self.app.test_client()

    	# The cleanup and schema creation
    	db.session.close()
    	db.drop_all()
    	db.create_all()

    	# The test fixtures (Ideally this would sit under a separate fixtures modules)
    	testData = [
    		(
                'Cricket', 
                'Australia Vs Ireland', 
                datetime(2018, 11, 23, 10, 10, 10), 
                [('Australia', 1.01), ('Ireland', 1.01)]
            ),
    		(
                'Football', 
                'Spain Vs Germany', 
                datetime(2018, 11, 22, 10, 10, 10), 
                [('Spain', 1.01), ('Germany', 1.01)]
            ),
            (
                'Football', 
                'Portugal Vs Italy', 
                datetime(2018, 11, 21, 10, 10, 10), 
                [('Portugal', 1.01), ('Italy', 1.01)]
            )
    	]
        for sportName, eventName, eventTime, selections in testData:
			sport = getOrCreate(db.session, Sport, name=sportName)
			event = Event(
                name=eventName,
                startTime=eventTime, 
                sport=sport
            )
			market = Market(name='Winner', event=event)
			for selName, odds in selections:
				db.session.add(Selection(name=selName, odds=odds, market=market))
    	db.session.commit()

    
    def testMatchByValidId(self):
        """This test asserts that when a valid match id is passed the service
        reponds with appropriate match information
        """
        expected = {
            'name': 'Australia Vs Ireland', 
            'url': 'http://localhost:5000/api/match/1', 
            'startTime': '2018-11-23 10:10:10', 
            'sport': {
                'id': 1, 
                'name': 'Cricket'
            }, 
            'markets': [
                {
                    'selections': [
                        {'odds': 1.01, 'id': 1, 'name': 'Australia'}, 
                        {'odds': 1.01, 'id': 2, 'name': 'Ireland'}
                    ], 
                    'id': 1, 
                    'name': 'Winner'
                }
            ], 
            'id': 1
        }

        response =  self.client.get('http://localhost:5000/api/match/1').data
        actual = json.loads(response)
        self.assertDictEqual(actual, expected)


    def testMatchByInvalidId(self):
        """Assert that the service responds appropriately when invalid match 
        id is sent
        """
        response =  self.client.get('http://localhost:5000/api/match/404')
        self.assertEqual(response.status_code, 404)


    def testMatchesBySportNameDefaultOrdering(self):
        """Check that we are only returned events that belong to the desired sport
        and that the default ordering is by name asc"""
        expected = {
            'matches': [
                {
                    'url': 'http://localhost:5000/api/match/3', 
                    'id': 3, 
                    'startTime': '2018-11-21 10:10:10', 
                    'name': 'Portugal Vs Italy'
                },
                {
                    'url': 'http://localhost:5000/api/match/2', 
                    'id': 2, 
                    'startTime': '2018-11-22 10:10:10', 
                    'name': 'Spain Vs Germany'
                }
            ]
        }
        response = self.client.get('http://localhost:5000/api/match/football').data
        actual = json.loads(response)
        self.assertEqual(actual, expected)


    def testMatchesBySportNameOrderedByStartTime(self):
        """Check that we are only returned events that belong to the desired sport
        and that the ordering for startTime is desc"""
        expected = {
            'matches': [
                {
                    'url': 'http://localhost:5000/api/match/2', 
                    'id': 2, 
                    'startTime': '2018-11-22 10:10:10', 
                    'name': 'Spain Vs Germany'
                },
                {
                    'url': 'http://localhost:5000/api/match/3', 
                    'id': 3, 
                    'startTime': '2018-11-21 10:10:10', 
                    'name': 'Portugal Vs Italy'
                }
            ]
        }
        response = self.client.get(
            'http://localhost:5000/api/match/football',
            query_string={'ordering': 'startTime'}
        ).data
        actual = json.loads(response)
    	self.assertEqual(actual, expected)


    def testMatchesByInvalidSportName(self):
        """Test that the service responds appropriately when invalid sport name is supplied
        """
        response = self.client.get('http://localhost:5000/api/match/cooking')
        self.assertEqual(response.status_code, 404)


    def testMatchByValidName(self):
        """Test that we can retrieve all matches for a given event name"""
        expected = {
            'matches' : [
                {
                    'url': 'http://localhost:5000/api/match/3', 
                    'id': 3, 
                    'startTime': '2018-11-21 10:10:10', 
                    'name': 'Portugal Vs Italy'
                }
            ]
        }
        response = self.client.get(
            'http://localhost:5000/api/match/', 
            query_string={'name': 'Portugal Vs Italy'}
        ).data

        actual = json.loads(response)
        self.assertEqual(actual, expected)


    def testMatchByInvalidName(self):
        """Test that we get an empty list if the name is invalid"""
        response = self.client.get(
            'http://localhost:5000/api/match/', 
            query_string={'name': 'Vim Vs Emacs'}
        ).data
        actual = json.loads(response)
        self.assertEqual(actual, {'matches': []})


    def testCreateNewEventHappyFlow(self):
        """When all information supplied is correct, assert that we are able
        to create an event successfull
        """
        payload = {
            'message_type': 'NewEvent',
            'event': {
                'name': 'Celta de Vigo vs Eibar',
                'startTime': str(datetime(2018, 11, 22, 22, 40, 0)),
                'sport': {'id': 2, 'name': 'Football'},
                'markets': [
                    {
                        'name': 'Winner',
                        'selections': [
                            {'name': 'Celta de Vigo', 'odds': 1.01}, 
                            {'name': 'Eibar', 'odds': 1.01}
                        ]
                    }
                ]
            }
        }
        response = self.client.post(
            'http://localhost:5000/api/match/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        # Check if new event was created
        newEventData = self.client.get(
            'http://localhost:5000/api/match/', 
            query_string={'name': 'Celta de Vigo vs Eibar'}
        ).data
        actual = json.loads(newEventData)
        expectedNewEventData = {
            'matches': [
                {
                    'url': 'http://localhost:5000/api/match/4', 
                    'id': 4, 
                    'startTime': '2018-11-22 22:40:00', 
                    'name': 'Celta de Vigo vs Eibar'
                }
            ]
        }
        self.assertEqual(actual, expectedNewEventData)


    def testCreateNewEventWithInvalidSportId(self):
        """Assert that when the payload contain invalid sport id, the service
        responses with 404
        """
        payload = {
            'message_type': 'NewEvent',
            'event': {
                'name': 'Celta de Vigo vs Eibar',
                'startTime': str(datetime(2018, 11, 22, 22, 40, 0)),
                'sport': {'id': 420, 'name': 'Football'},
                'markets': [
                    {
                        'name': 'Winner',
                        'selections': [
                            {'name': 'Celta de Vigo', 'odds': 1.01}, 
                            {'name': 'Eibar', 'odds': 1.01}
                        ]
                    }
                ]
            }
        }
        response = self.client.post(
            'http://localhost:5000/api/match/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)


    def testUpdateOddsHappyFlow(self):
        payload = {
            'message_type': 'UpdateOdds',
            'event':{
                'name': 'Australia Vs Ireland', 
                'url': 'http://localhost:5000/api/match/1', 
                'startTime': '2018-11-23 10:10:10', 
                'sport': {
                    'id': 1, 
                    'name': 'Cricket'
                }, 
                'markets': [
                    {
                        'selections': [
                            {'odds': 9.09, 'id': 1, 'name': 'Australia'}, 
                            {'odds': 1.01, 'id': 2, 'name': 'Ireland'}
                        ], 
                        'id': 1, 
                        'name': 'Winner'
                    }
                ], 
                'id': 1
            }
        }
        response = self.client.post(
            'http://localhost:5000/api/match/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)
        # Get the event again to check if odds were actually updated
        updatedEventData = self.client.get('http://localhost:5000/api/match/1').data
        actual = json.loads(updatedEventData)
        expectedUpdatedEventData = [
            {'odds': 9.09, 'id': 1, 'name': 'Australia'}, 
            {'odds': 1.01, 'id': 2, 'name': 'Ireland'}
        ]
        self.assertEqual(actual['markets'][0]['selections'], expectedUpdatedEventData)


    def testUpdateOddInvalidEventId(self):
        payload = {
            'message_type': 'UpdateOdds',
            'event':{
                'name': 'Australia Vs Ireland', 
                'url': 'http://localhost:5000/api/match/1', 
                'startTime': '2018-11-23 10:10:10', 
                'sport': {
                    'id': 1, 
                    'name': 'Cricket'
                }, 
                'markets': [
                    {
                        'selections': [
                            {'odds': 9.09, 'id': 1, 'name': 'Australia'}, 
                            {'odds': 1.01, 'id': 2, 'name': 'Ireland'}
                        ], 
                        'id': 1, 
                        'name': 'Winner'
                    }
                ], 
                'id': 123
            }
        }
        response = self.client.post(
            'http://localhost:5000/api/match/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
