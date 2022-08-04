#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
from models import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

#----------------------------------------------------------------------------#
# Models.
#-----------------All models have been moved to models.py file and imported above-----------------------------------------------------------#


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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  all_regions = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

# Looping across all regions
  
  for region in all_regions:
    region_venues = Venue.query.filter_by(state=region.state).filter_by(city=region.city).all()
    venue_data = []
    for venue in region_venues:
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
        })
# Appending a dictionary of data to the data list variable created above.

      data.append({
      "city": region.city,
      "state": region.state,
      "venues": venue_data
    })
      
# render result to the view.

  return render_template('pages/venues.html', regions=data);

      
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search_finding = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()

# create empty list

  data = []
  
# Loop through search findings and append the id and name to the empty data list as a dictionary

  for result in search_finding:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })

  response={
    "count": len(search_finding),
    "data": data
  }

# render result to view
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

  # SUCCESS: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  if not venue:
    return render_template('errors/404.html')

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  
  upcoming_shows = []

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

    data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows,
    "upcoming_shows_count": len(upcoming_shows),
    "past_shows_count": len(past_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

  # shows the venue page with the given venue_id
  # SUCCESS: replace with real venue data from the venues table, using venue_id

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
# Add and commit the following changes
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
# except and error occured then execute the except block
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
# ensure that the session closes irrespective of what the case may be
  finally:
    db.session.close()

# what should be flashed if an error did/did not occur
  if error:
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

# render to the view
  return render_template('pages/home.html')

  
  # SUCCESS: insert form data as a new Venue record in the db, instead
  # SUCCESS: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # SUCCESS: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred. Venue {venue_id} could not be deleted.')
  if not error:
    flash(f'Venue {venue_id} was successfully deleted.')
  return render_template('pages/home.html')
  # SUCCESS: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = db.session.query(Artist).all()
  
  return render_template('pages/artists.html', artists=data)
# SUCCESS: replace with real data returned from querying the database

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search_finding = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in search_finding:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })

  response={
    "count": len(search_finding),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# SUCCESS: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals","Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_inquiry = db.session.query(Artist).get(artist_id)

  if not artist_inquiry:
    return render_template('errors/404.html')

  past_shows_inquiry = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  past_shows = []

  for show in past_shows_inquiry:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  upcoming_shows_inquiry = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_shows_inquiry:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

    data = {
    "id": artist_query.id,
    "name": artist_query.name,
    "genres": artist_query.genres,
    "city": artist_query.city,
    "state": artist_query.state,
    "phone": artist_query.phone,
    "website": artist_query.website,
    "facebook_link": artist_query.facebook_link,
    "seeking_venue": artist_query.seeking_venue,
    "seeking_description": artist_query.seeking_description,
    "image_link": artist_query.image_link,
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows,
    "upcoming_shows_count": len(upcoming_shows),
    "past_shows_count": len(past_shows),
  }

  return render_template('pages/show_artist.html', artist=data)
  # shows the artist page with the given artist_id
  # SUCCESS: replace with real artist data from the artist table, using artist_id


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if not artist:
    flash("This artist does not exist.")
    return render_template("errors/404.html")

  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)
  # SUCCESS: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  artistData = ArtistForm(request.form)
  genresList = request.form.getlist("genres")
  
  try:
    artist.name = artistData.name.data
    artist.city = artistData.city.data
    artist.state = artistData.state.data
    artist.phone = artistData.phone.data
    artist.genres = ",".join(genresList)
    artist.facebook_link = artistData.facebook_link.data
    artist.image_link = artistData.image_link.data
    artist.website = artistData.website.data
    artist.seeking_venue = artistData.seeking_venue.data
    artist.seeking_description = artistData.seeking_description.data

    db.session.commit()
 # on successful db update, flash success
    flash("Artist: " + artistData.name.data + " has been successfully updated!")
  except:
    db.session.rollback()
    print(sys.exc_info())
# Done: on unsuccessful db update, flash an error instead.
    flash(
      "An error occurred. Artist "
      + artistData.name.data
      + " could not be updated."
        )
  finally:
    db.session.close()
  return redirect(url_for("show_artist", artist_id=artist_id))

  # SUCCESS: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = venue.query.get(venue_id)
  
  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

# SUCCESS: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred. Venue could not be changed.')
  if not error:
    flash(f'Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))
  # SUCCESS: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres'),
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # SUCCESS: on unsuccessful db insert, flash an error instead.
  if error:
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  # on successful db insert, flash success
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # SUCCESS: insert form data as a new Venue record in the db, instead
  # SUCCESS: modify data to be the data object returned from db insertion


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows_inquiry = db.session.query(Show).join(Artist).join(Venue).all()

  data = []
  for show in shows_inquiry:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    print(request.form)

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # SUCCESS: on unsuccessful db insert, flash an error instead.
  if error:
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed')
  return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form
  # SUCCESS: insert form data as a new Show record in the db, instead

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
