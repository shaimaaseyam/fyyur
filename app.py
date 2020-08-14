#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from models import db, Venue, Artist, Shows
import datetime
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
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/fyyur'


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



    
    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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

  current_time = datetime.now()
  venues = Venue.query.order_by('id').all()
  data = []
  
  for n in venues:
    venue = {
      "city":n.city,
      "state":n.state,"venues": [{
        "id": n.id,
        "name":n.name,
      }]
      }
    data.append(venue)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term=request.form.get('search_term', '')
  searchVenue=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data=[]
  for x in searchVenue:
    search={
      'id':x.id,
      'name':x.name,
    }
    data.append(search)

  response={
    "count": len(searchVenue),
    "data": data,
  } 

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first()
  current_time = datetime.now()
  pastShows = Shows.query.filter(Shows.venue_id == venue_id).filter(Shows.start_time < str(datetime.now())).all()
  upcoming = Shows.query.filter(Shows.venue_id == venue_id).filter(Shows.start_time > str(datetime.now())).all()
  past_shows = []
  for n in pastShows:
    past_shows.append({
      "artist_id": n.artist_id,
      "artist_name": (Artist.query.filter_by(id=n.artist_id).first()).name,
      "artist_image_link": Artist.query.filter_by(id=n.artist_id).first().image_link,
      "start_time": n.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })
  
  data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_artist": venue.seeking_artist,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": [],
      "past_shows_count": len(pastShows),
      "upcoming_shows_count": len(upcoming),
    }
 
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error=False
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.get('genres', '')
    address = request.form.get('address', '')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    image_link = request.form.get('image_link', '')
    seeking_description = request.form.get('seeking_description', '')
    seeking_artist = request.form.get('seeking_artist')
    venues = Venue(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      address=address,
      facebook_link=facebook_link,
      website_link=website_link,
      image_link=image_link,
      seeking_description=seeking_description,
      seeking_artist=bool(seeking_artist)
      )
    db.session.add(venues)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  getartists=Artist.query.order_by('id').all()
  data=[]
  for n in getartists:
    new_data={'id':n.id, 'name':n.name}
    data.append(new_data)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  searchArtists=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data=[]
  for x in searchArtists:
    search={
      'id':x.id,
      'name':x.name,
    }
    data.append(search)

  response={
    "count": len(searchArtists),
    "data": data,
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artists = Artist.query.filter_by(id=artist_id).first()
  current_time = datetime.now()
  pastShows = Shows.query.filter(Shows.artist_id == artist_id).filter(Shows.start_time < str(datetime.now())).all()
  upcoming = Shows.query.filter(Shows.artist_id == artist_id).filter(Shows.start_time > str(datetime.now())).all()
  past_shows = []
  for n in pastShows:
    past_shows.append({
      "venue_id": n.venue_id,
      "venue_name": (Venue.query.filter_by(id=n.venue_id).first()).name,
      "venue_image_link": Venue.query.filter_by(id=n.venue_id).first().image_link,
      "start_time": n.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })
  
  data={
      "id": artists.id,
      "name": artists.name,
      "genres": artists.genres,
      "city": artists.city,
      "state": artists.state,
      "phone": artists.phone,
      "website": artists.website_link,
      "facebook_link": artists.facebook_link,
      "seeking_venue": artists.seeking_venue,
      "seeking_description": artists.seeking_description,
      "image_link": artists.image_link,
      "past_shows": past_shows,
      "upcoming_shows": [],
      "past_shows_count": len(pastShows),
      "upcoming_shows_count": len(upcoming),
    }
    
    
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error=False
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.get('genres', '')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    image_link = request.form.get('image_link', '')
    seeking_description = request.form.get('seeking_description', '')
    seeking_venue = request.form.get('seeking_venue')
    artists = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link,
      website_link=website_link,
      image_link=image_link,
      seeking_description=seeking_description,
      seeking_venue=bool(seeking_venue)
      )
    db.session.add(artists)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist '+ request.form['name']+ ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist'))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  getshows=Shows.query.all()
  getvenue=Venue.query.all()
  getartist=Artist.query.all()
  data=[]
  for n in getshows:
    data.append({
      "venue_id": n.venue_id,
      "venue_name": Venue.query.filter_by(id=n.venue_id).first().name,
      "artist_id":  n.artist_id,
      "artist_name": Artist.query.filter_by(id=n.artist_id).first().name,
      "artist_image_link": Artist.query.filter_by(id=n.artist_id).first().image_link,
      "start_time": str(n.start_time)
    })
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error=False
  try:
    artist_id = request.form.get('artist_id', '')
    venue_id = request.form.get('venue_id', '')
    start_time = request.form.get('start_time', '')
    shows = Shows(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
      )
    db.session.add(shows)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
   flash('Show was successfully listed!')
  return render_template('pages/home.html')
  
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
