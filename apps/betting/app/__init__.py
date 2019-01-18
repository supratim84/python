#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains the application's data models. SQLAlchemy used to define relations
between various models and sqlite to facilitate storage.
author: supratim.ghosh1@gmail.com
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask

import datetime
import os

# Initiate the orm
myApp = Flask(__name__)
db = SQLAlchemy(myApp)


class DevConfig:
    """Defines the development enviroment basic configurations
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/dev.db' % os.getcwd()


def getOrCreate(session, model, **kwargs):
    """Based on the filter criteria, return a existing model instance
    or creates a new one.

    @param db.Session session: handle to the current session
    @param app.Model model: selected model class
    @param dict kwargs: containing the initializing parameters
    @return db.Model instance: model instance (new or existing) 
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def createApplication(addFixtures=False):
    """This method initializes the flask application and set the configuration
    (hard coded to use dev only for now).

    @param bool addFixtures: This is a one time setup used for demo purposes
    to populated some data in sqlite so that the GETs work right away
    @return flask.Application: returns the configured flask application instance
    """
    myApp.config.from_object(DevConfig())
    db.init_app(myApp)
    migrate = Migrate(myApp, db)
    from app import models

    # For demo puposes only, if you are happy to call a bunch of POSTs before checking the GETs
    # out then this can be deleted.
    if addFixtures:

        with myApp.app_context():
            db.metadata.create_all(db.engine)
            for eName, eTime in [
                ('Real Madrid vs Barcelona', datetime.datetime(2018, 6, 20, 10, 30, 0)),
                ('Cavaliers vs Lakers', datetime.datetime(2018, 1, 15, 22, 0, 0)),
            ]:
                sport = getOrCreate(db.session, models.Sport, name='Football')
                event = models.Event(name=eName, startTime=eTime, sport=sport)
                market = models.Market(name='Winner', event=event)

                sel1Name, _, sel2Name = eName.partition(' vs ')
                selection1 = models.Selection(name=sel1Name, odds=1.01, market=market)
                selection2 = models.Selection(name=sel2Name, odds=1.01, market=market)
                
                db.session.add(selection1)
                db.session.add(selection2)
            db.session.commit()
    
    return myApp
