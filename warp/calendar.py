import flask
import string
import random

from warp.db import CalenderRef, Users, SeatAssign, Seat, Book, Zone
from . import utils
import peewee
from . import blob_storage

from icalendar import Calendar, Event, vText
from datetime import datetime
from zoneinfo import ZoneInfo


bp = flask.Blueprint('calendar', __name__)


def generate_random_key(length=32):
    """Generate a random key of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_first(query):
    """Get the first result from a query."""
    for item in query:
        return item
    return None


def decode_calendar(cal):
    return cal.to_ical().decode("utf-8").replace('\r\n', '\n').strip()


@bp.route("/calendar/feed/<uid>-<key>/feed.ics")
def feed(uid, key):
    """Get calendar feed."""
    res = get_first(
        CalenderRef.select().where(CalenderRef.id == uid)
    )
    if res['hash'] != key:
        flask.abort(404)

    fromTS = utils.getRelativeDay(-7)
    timeRange = utils.getTimeRange(extended=True)
    toTS = timeRange["toTS"]

    results = Book.select(
        Book.id, Seat.name, Book.fromts, Book.tots,
        peewee.Value(Zone.name).alias("zone_name")
    ).join(
        Users, on=(Book.login == Users.login)
    ).join(
        Seat, on=(Book.sid == Seat.id)
    ).join(
        Zone, on=(Seat.zid == Zone.id)
    ).where(
        (Users.login == res['login'])
        & (Book.fromts < toTS) & (Book.tots > fromTS)
    )

    cal = Calendar()
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("prodid", "-//WARP//WARP Calendar//EN")
    cal.add("method", "PUBLISH")
    cal.add("X-WR-TIMEZONE", "UTC")

    # Set the calendar's timezone
    # timezone = ZoneInfo("Europe/Brussels")
    timezone = ZoneInfo("UTC")  # Use UTC for simplicity
    calendar_time = datetime.fromtimestamp(
        timeRange["fromTS"], tz=timezone
    )
    # Hacky solution to go to belgium timezone...
    for res in results:
        event = Event()
        event.add('summary', f"WARP {res['zone_name']} - SEAT {res['name']}")
        event.add(
            'dtstart', datetime.fromtimestamp(res['fromts'] - 3600*2, tz=timezone)
        )
        event.add('dtend', datetime.fromtimestamp(res['tots'] - 3600*2, tz=timezone))
        event.add('dtstamp', calendar_time)
        event.add("description", "WARP reservation")
        event['uid'] = f"{res['id']}bookingwarp"
        event['url'] = "https://194-146-38-110.cloud-xip.com/"
        cal.add_component(event)

    ret = flask.make_response(decode_calendar(cal))
    ret.mimetype = "text/calendar"
    return ret


def get_calendar_info():
    """View and if not there, create calendar feed."""
    login = flask.g.login  # User login
    res = get_first(
        CalenderRef.select().where(CalenderRef.login == login)
    )
    if res is None:
        hash = generate_random_key(length=64)
        res = CalenderRef.insert(
            login=login,
            hash=hash
        ).execute()

    return res
