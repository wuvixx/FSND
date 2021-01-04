#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
import os
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
	date = dateutil.parser.parse(value)
	if format == 'full':
		format="EEEE MMMM, d, y 'at' h:mma"
	elif format == 'medium':
		format="EE MM, dd, y h:mma"
	return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
	recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
	recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
	recent_artists_data = [((a.id,a.name,'') if len(recent_artists)-i==1 else (a.id,a.name,'|')) for i,a in enumerate(recent_artists)]
	recent_venues_data = [((v.id,v.name,'') if len(recent_venues)-i==1 else (v.id,v.name,'|')) for i,v in enumerate(recent_venues)]
	return render_template('pages/home.html', recent={'artists': recent_artists_data, 'venues': recent_venues_data})


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
	venue_query = Venue.query.all()
	data = []
	for venue in venue_query:
		state = next(filter(lambda s: s['state'] == venue.state, data), None)
		if not state:
			data.append({
				'city': venue.city,
				'state': venue.state,
				'venues': [{
				'id': venue.id,
				'name': venue.name,
				'num_upcoming_shows': 0
			}]
		})
		else:
			state['venues'].append({
				'id': venue.id,
				'name': venue.name,
				'num_upcoming_shows': 0
			})
	return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
	venue_query = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
	response = {
		'count': len(venue_query),
		'data': []
	}
	for venue in venue_query:
		response['data'].append({'id': venue.id, 'name': venue.name})
	return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	q = db.session.query(Venue, Show, Artist).outerjoin(Show, (Venue.id == venue_id) & (Venue.id == Show.venue_id)).outerjoin(Artist, Artist.id == Show.artist_id).filter(Venue.id==venue_id).all()
	upcoming_shows = []
	past_shows = []
	for d in q:
		if d[2]:
			artist_data = {
				'artist_id': d[2].id,
				'artist_name': d[2].name,
				'artist_image_link': d[2].image_link,
				'start_time': str(d[1].startTime)
			}
			past_shows.append(artist_data) if datetime.now() > d[1].startTime else upcoming_shows.append(artist_data)
	data = {
		'id': q[0][0].id,
		'name': q[0][0].name,
		'genres': str(q[0][0].genres).split(','),
		'address': q[0][0].address,
		'city': q[0][0].city,
		'state': q[0][0].state,
		'phone': q[0][0].phone,
		'website': q[0][0].website,
		'facebook_link': q[0][0].facebook_link,
		'seeking_talent': q[0][0].seeking_talent,
		'seeking_description': q[0][0].seeking_description,
		'image_link': q[0][0].image_link,
		'past_shows': past_shows,
		'upcoming_shows': upcoming_shows,
		'past_shows_count': len(past_shows),
		'upcoming_shows_count': len(upcoming_shows)
	}
	# data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
	return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
	form = VenueForm()
	return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
	try:
		new_venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'], phone=request.form['phone'], facebook_link=request.form['facebook_link'], genres=','.join(request.form.getlist('genres')))
		db.session.add(new_venue)
		db.session.commit()
		# on successful db insert, flash success
		flash('Venue ' + request.form['name'] + ' was successfully listed!')
	except:
		db.session.rollback()
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
		# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
	try:
		Venue.query.filter_by(id=venue_id).delete()
		db.session.commit()
		flash('Venue has been deleted.')
	except:
		db.session.rollback()
		flash('An error occurred. Could not delete.')
	return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	artist_query = Artist.query.all()
	data = []
	for artist in artist_query:
		data.append({'id': artist.id, 'name': artist.name})
	return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
	artist_query = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
	response = {
		'count': len(artist_query),
		'data': []
	}
	for artist in artist_query:
		response['data'].append({'id': artist.id, 'name': artist.name})
	return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	q = db.session.query(Artist, Show, Venue).outerjoin(Show, (Artist.id == artist_id) & (Artist.id == Show.artist_id)).outerjoin(Venue, Venue.id == Show.venue_id).filter(Artist.id==artist_id).all()
	upcoming_shows = []
	past_shows = []
	for d in q:
		if d[2]:
			venue_data = {
				'venue_id': d[2].id,
				'venue_name': d[2].name,
				'venue_image_link': d[2].image_link,
				'start_time': str(d[1].startTime)
			}
			past_shows.append(venue_data) if datetime.now() > d[1].startTime else upcoming_shows.append(venue_data)
	data = {
		'id': q[0][0].id,
		'name': q[0][0].name,
		'genres': q[0][0].genres.split(','),
		'city': q[0][0].city,
		'state': q[0][0].state,
		'phone': q[0][0].phone,
		'seeking_venue': q[0][0].seeking_venue,
		'image_link': q[0][0].image_link,
		'past_shows': past_shows,
		'upcoming_shows': upcoming_shows,
		'past_shows_count': len(past_shows),
		'upcoming_shows_count': len(upcoming_shows)
	}
	# data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
	return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	form = ArtistForm()
	q = Artist.query.get(artist_id)
	artist = {
		'id': q.id,
		'name': q.name,
		'genres': q.genres,
		'city': q.city,
		'state': q.state,
		'phone': q.phone,
		'facebook_link': q.facebook_link,
		'seeking_venue': q.seeking_venue,
		'image_link': q.image_link
	}
	return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	try:
		q = Artist.query.get(artist_id)
		q.name = request.form['name']
		q.city = request.form['city']
		q.state = request.form['state']
		q.phone = request.form['phone']
		q.genres = request.form['genres']
		q.facebook_link = request.form['facebook_link']
		db.session.commit()
	except:
		db.session.rollback()
	return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()
	q = Venue.query.get(venue_id)
	venue = {
		'id': q.id,
		'name': q.name,
		'genres': q.genres,
		'address': q.address,
		'city': q.city,
		'state': q.state,
		'phone': q.phone,
		'website': q.website,
		'facebook_link': q.facebook_link,
		'seeking_talent': q.seeking_talent,
		'seeking_description': q.seeking_description,
		'image_link': q.image_link
	}
	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	try:
		q = Venue.query.get(venue_id)
		q.name = request.form['name']
		q.city = request.form['city']
		q.state = request.form['state']
		q.address = request.form['address']
		q.phone = request.form['phone']
		q.genres = request.form['genres']
		q.facebook_link = request.form['facebook_link']
		db.session.commit()
	except:
		db.session.rollback()

	return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
	form = ArtistForm()
	return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
	try:
		new_venue = Artist(name=request.form['name'], city=request.form['city'], state=request.form['state'], phone=request.form['phone'], facebook_link=request.form['facebook_link'], genres=','.join(request.form.getlist('genres')))
		db.session.add(new_venue)
		db.session.commit()
		# on successful db insert, flash success
		flash('Artist ' + request.form['name'] + ' was successfully listed!')
	except:
		db.session.rollback()
		flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
		# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
	shows = Show.query.all()
	data = []
	for show in shows:
		artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
		venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
		data.append({
			'venue_id': venue.id,
			'venue_name': venue.name,
			'artist_id': artist.id,
			'artist_name': artist.name,
			'artist_image_link': artist.image_link,
			'start_time': str(show.startTime)
		})
	return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	try:
		new_show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'], startTime=request.form['start_time'])
		db.session.add(new_show)
		db.session.commit()
		flash('Show was successfully listed!')
	except:
		db.session.rollback()
		flash('An error has occurred. Please make sure you\'ve entered a correct artist and venue.')
	return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
	return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
	return render_template('errors/500.html'), 500


if not app.debug:
	file_handler = FileHandler('error.log')
	file_handler.setFormatter(
		Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
	)
	app.logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
	# app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
'''
