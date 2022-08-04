from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, 
                  render_template, 
                  request, Response, flash, redirect, url_for, jsonify, abort)
                  
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    shows = db.relationship('Show', backref="venue", lazy=True)

    def __repr__(self):
        return '<Venue {}>'.format(self.name)


class Artist(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    genres = db.Column(db.ARRAY(db.String))
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="artist", lazy=True)

    def __repr__(self):
        return '<Artist {}>'.format(self.name)


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Show {}{}>'.format(self.artist_id, self.venue_id)
