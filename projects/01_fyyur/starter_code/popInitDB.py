

from app import Venue, Show
from collections import defaultdict
from datetime import datetime, timedelta

venues = Venue.query.all()

venues_by_city_state = defaultdict(list)

now = datetime.now() - timedelta(days=5)

for venue in venues:
    num_upcoming_shows = len([show for show in venue.shows if show.start_time > now])
    venues_by_city_state[(venue.city, venue.state)].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': num_upcoming_shows,
    })

data = [{'city': city, 'state': state, 'venues': venues} for (city, state), venues in venues_by_city_state.items()]

print(data)
