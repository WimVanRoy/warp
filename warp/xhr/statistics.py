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
    future = utils.getRelativeDay(5) - 1
    past = utils.getRelativeDay(-30) + 1
    query = Book.select(Book.id, Book.fromts, Book.tots) \
        .where(Book.fromts >= past) \
        .where(Book.tots <= future).order_by(Book.fromts)

    # Count by day:
    data = []
    time = past
    count = 0
    for b in query:
        if b['fromts'] < time + 24*3600:
            count += 1
        else:
            data.append({"date": strftime("%Y-%m-%d", gmtime(time)), "count": count})
            while time + 24*3600 < b['fromts']:
                time += 24*3600
                data.append({"date": strftime("%Y-%m-%d", gmtime(time)), "count": 0})
            count = 1

    data.append({"date": strftime("%Y-%m-%d", gmtime(time)), "count": count})
    while time < future:
        time += 24*3600
        data.append({"date": strftime("%Y-%m-%d", gmtime(time)), "count": 0})

    res = {"data": data}
    print(res)

    return flask.current_app.response_class(
        response=orjson.dumps(res),
        status=200,
        mimetype='application/json')
