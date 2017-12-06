import sqlite3
from entity.feed import Feed
from vendor.bottle import *


class RSSReaderApplication:

    def __init__(self):
        self.db = None

    def init_db(self):
        self.db = sqlite3.connect(':memory:')
        c = self.db.cursor()
        with open('migration.sql', 'r+') as migration_file:
            statements = migration_file.read().replace('\n', '').split(';')
            for stmt in statements:
                c.execute(stmt)
        c.close()

    def run(self):
        self.init_db()
        run(host='localhost', port=8080)


# web endpoint
@route('/')
def index():
    feed = Feed(app.db)
    feed_list = feed.get_list()
    return template('views/index.html', {'feed_list': feed_list})


@post('/rss/add')
def rss_add():
    r_url = request.forms.get('link')
    f = Feed(app.db)
    f_id = f.exists(r_url)
    if f_id is False:
        f_id = f.create(r_url)
        if f_id is False:
            return redirect('/rss/error')

    return redirect('/rss/view/' + str(f_id))


@route('/rss/view/<id>')
def rss_view(id):
    f = Feed(app.db)
    page = request.query.get('page')
    if page is None:
        page = 0

    data = f.get_items(id, page)
    if data is False or data['count'] == 0:
        return redirect('/')

    return template('views/view.html', {'fid': id, 'data': data, 'page': int(page), 'feed_list': f.get_list()})


@route('/rss/error')
def rss_error():
    feed = Feed(app.db)
    feed_list = feed.get_list()
    return template('views/error.html', {'feed_list': feed_list})


@post('/rss/update')
def rss_update():
    f_id = request.forms.get('feed_id')
    f = Feed(app.db)
    f.update(f_id)
    return redirect('/rss/view/' + str(f_id))


@route('/static/<path:path>')
def static_request(path):
    return static_file(path, root='static')


if __name__ == "__main__":
    app = RSSReaderApplication()
    app.run()
