from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
	__tablename__ = 'show'

	artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete="CASCADE"), primary_key=True)
	venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete="CASCADE"), primary_key=True)
	startTime = db.Column(db.DateTime)

class Venue(db.Model):
	__tablename__ = 'venue'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	address = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	genres = db.Column(db.String(120))
	image_link = db.Column(db.String(500), default="../static/img/defaultvenue.jpg")
	facebook_link = db.Column(db.String(120))
	website = db.Column(db.String(120))
	seeking_talent = db.Column(db.Boolean())
	seeking_description = db.Column(db.String(120))
	_artists = db.relationship('Artist', secondary='show', backref=db.backref('venues', lazy='dynamic', passive_deletes=True))

class Artist(db.Model):
	__tablename__ = 'artist'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	genres = db.Column(db.String(120))
	image_link = db.Column(db.String(500), default="../static/img/defaultavatar.png")
	facebook_link = db.Column(db.String(120))
	seeking_venue = db.Column(db.Boolean())
	_venues = db.relationship('Venue', secondary='show', backref=db.backref('artists', lazy='dynamic'), passive_deletes=True)