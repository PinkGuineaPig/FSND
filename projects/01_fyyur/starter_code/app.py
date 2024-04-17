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
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate

from collections import defaultdict
from datetime import datetime, timedelta

from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

#def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
#  if format == 'full':
#      format="EEEE MMMM, d, y 'at' h:mma"
#  elif format == 'medium':
#      format="EE MM, dd, y h:mma"
#  return babel.dates.format_datetime(date, format, locale='en')
def format_datetime(value, format='medium'):
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format)

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()

  # Create a dictionary to hold the venues for each city and state
  venues_by_city_state = defaultdict(list)

  # Get the current time
  now = datetime.now() - timedelta(days=5)

  # Iterate over the venues
  for venue in venues:
      # Calculate the number of upcoming shows for this venue
      num_upcoming_shows = len([show for show in venue.shows if show.start_time > now])

      # Append the venue to the appropriate city and state's list
      venues_by_city_state[(venue.city, venue.state)].append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': num_upcoming_shows,
      })

    # Convert the defaultdict back into a regular dict and format it as a list of dicts

  data = [{'city': city, 'state': state, 'venues': venues} for (city, state), venues in venues_by_city_state.items()]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term')
  search_results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()  # search results by ilike matching partern to match every search term

  dat = []

  for v in search_results:
    dat.append({
      "id" : v.id,
      "name": v.name,
      "num_upcoming_shows": 3,
    })

  response={
    "count": len(search_results),
    "data": dat
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = venue.shows

  now = datetime.now()

  past_shows = [show for show in shows if show.start_time <= now]
  future_shows = [show for show in shows if show.start_time > now]

  past_shows_dict = []
  future_shows_dict = []

  for show in past_shows:
    past_shows_dict.append(
      {
        'venue_id': show.artist_id ,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time
      }
    )

  for show in future_shows:
    future_shows_dict.append(
      {
        'venue_id': show.artist_id ,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time
      }
    )

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_dict,
    "upcoming_shows": future_shows_dict,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(future_shows),
  }

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  venue = Venue(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,

    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
     
    genres = form.genres.data 
  )

  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully listed!')
    return redirect(url_for('venues'))
  except SQLAlchemyError as e:
      flash(str(e))
      return redirect(url_for('venues'))  # Redirect back to the form
  finally:
      db.session.close()

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  search_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()  # search results by ilike matching partern to match every search term

  dat = []

  for v in search_results:
    dat.append({
      "id" : v.id,
      "name": v.name,
      "num_upcoming_shows": 3,
    })

  response={
    "count": len(search_results),
    "data": dat
  }

  return render_template('pages/search_artists.html',results=response,search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id


  db.session.query()

  artist = Artist.query.get(artist_id)
  shows = artist.shows

  now =  datetime.now()

  past_shows = [show for show in shows if show.start_time <= now]
  future_shows = [show for show in shows if show.start_time > now]

  past_shows_dict = []
  future_shows_dict = []

  for show in past_shows:
    past_shows_dict.append(
      {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time
      }
    )

  for show in future_shows:
    future_shows_dict.append(
      {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time
      }
    )

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_dict,
    "upcoming_shows": future_shows_dict,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(future_shows),
  }

  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artst = Artist.query.get(artist_id)

  form = ArtistForm()
  form.name.data = artst.name
  form.city.data = artst.city
  form.state.data = artst.state
  form.phone.data = artst.phone
  form.image_link.data = artst.image_link
  form.genres.data = artst.genres,
  form.facebook_link.data = artst.facebook_link
  form.website_link.data = artst.website_link
  form.seeking_venue.data = artst.seeking_venue
  form.seeking_description.data = artst.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>

  return render_template('forms/edit_artist.html', form=form, artist=artst)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artst = Artist.query.get(artist_id)

  form = ArtistForm(request.form)

  if artst:
    artst.name = form.name.data
    artst.city = form.city.data
    artst.state = form.state.data
    artst.phone = form.phone.data
    artst.image_link = form.image_link.data
    artst.genres = form.genres.data
    artst.facebook_link = form.facebook_link.data
    artst.website_link = form.website_link.data
    artst.seeking_venue = form.seeking_venue.data
    artst.seeking_description = form.seeking_description.data

    try: 
      db.session.commit()
    except exc.SQLAlchemyError as e:
      db.session.rollback()
      flash('Issue Updating ' + form.name.data)
      print(str(e))

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)

  form = VenueForm()
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  if venue:
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data

  try:
    db.session.commit()
    flash('Commit successful')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred: ' + str(e))

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)
  artist = Artist(
      name = form.name.data,
      genres = form.genres.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      website_link = form.website_link.data,
      facebook_link = form.facebook_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data,
      image_link = form.image_link.data,
  )
  try:
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')
      return redirect(url_for('artists'))  # Redirect to the home page
  except:
      flash('An error occurred. Artist ' + form.name.data + 'could not be added')
      return redirect(url_for('artists'))  # Redirect back to the form
  finally:
      db.session.close()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  now = datetime.now()

  # Query the database for shows in the future
  future_shows = Show.query.filter(Show.start_time > now).all()

  locals = []
  results = db.session.query(Show, Venue, Artist).join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).order_by(Show.start_time.desc()).all()

  for show, venue, artist in results:  # 3 objects here!
      locals.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_time
      })

  return render_template('pages/shows.html', shows=locals)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success

  form = ShowForm(request.form)
  
  show = Show(
    artist_id = form.artist_id.data,
    venue_id = form.venue_id.data,
    start_time = form.start_time.data
  )

  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    return redirect(url_for('index'))
  except:
    flash('Show had issues in listing!')
    return redirect(url_for('index'))
  finally:
    db.session.close()



  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
