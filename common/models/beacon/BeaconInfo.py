# coding: utf-8
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class BeaconInfo(db.Model):
    __tablename__ = 'beacon_info'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), nullable=False, unique=True, server_default=db.FetchedValue())
    major = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    minor = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
