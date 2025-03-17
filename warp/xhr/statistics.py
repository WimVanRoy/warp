import flask
from jsonschema import validate
from warp import utils
import orjson
from time import strftime, gmtime

from warp.db import Book

bp = flask.Blueprint('statistics', __name__, url_prefix='statistics')


@bp.route("fetch", endpoint='fetch')
def fetch():
    """Fetch the data of the statistics."""
    future_endday = utils.getRelativeDay(7) - 1
    future_startday = utils.getRelativeDay(6)
    past = utils.getRelativeDay(-30)
    query = Book.select(Book.id, Book.fromts, Book.tots) \
        .where(Book.fromts >= past) \
        .where(Book.fromts <= future_endday).order_by(Book.fromts)

    # Count by day:
    data = []
    time = past
    count = 0
    for b in query:
        while b['fromts'] > time + 24*3600:
            data.append(
                {"date": strftime("%Y-%m-%d", gmtime(time)), "count": count})
            time += 24*3600
            count = 0

        count += 1

    data.append({"date": strftime("%Y-%m-%d", gmtime(time)), "count": count})
    while time < future_startday:
        time += 24*3600
        data.append({"date": strftime("%Y-%m-%d", gmtime(time)), "count": 0})

    res = {"data": data}
    return flask.current_app.response_class(
        response=orjson.dumps(res),
        status=200,
        mimetype='application/json')
