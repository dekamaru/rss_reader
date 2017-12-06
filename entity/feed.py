from entity.rss import RSS
import math

class Feed:

    def __init__(self, db):
        self.db = db
        self.url = None
        self.items = None

    def create(self, url):
        # if exists - error
        c = self.db.cursor()
        rss = RSS(url)
        if rss.parse() is False:
            return False

        c.execute('INSERT INTO feeds (`name`, url) VALUES (:n, :u)', {'n': rss.get_name(), 'u': url})
        c.execute('SELECT last_insert_rowid()')
        feed_id = c.fetchone()[0]
        self.push_items(feed_id, rss.get_items())
        return feed_id

    def update(self, feed_id):
        f_url = self._fetch_value('SELECT url FROM feeds WHERE rowid = :fid', {'fid': feed_id})
        rss = RSS(f_url)
        rss.parse()
        self.push_items(feed_id, rss.get_items())

    def push_items(self, feed_id, items):
        c = self.db.cursor()
        ins_sql = 'INSERT INTO feed_content (feed_id, url, title, categories, pub_date, description) VALUES (:fid, :u, :t, :c, :pd, :d)'
        for item in items:
            if not self.item_exist(item['link']):
                c.execute(ins_sql, {
                    'fid': feed_id,
                    'u': item['link'],
                    't': item['title'],
                    'c': ','.join(item['categories']),
                    'pd': item['date'].strftime('%Y-%m-%d %H:%M:%S'),
                    'd': item['description']
                })
        c.close()

    def _fetch_value(self, sql, data={}):
        c = self.db.cursor()
        c.execute(sql, data)
        data = c.fetchone()
        if data is None:
            return False
        else:
            return data[0]

    def get_items(self, feed_id, page = 0):
        ITEM_PER_PAGE = 5

        c = self.db.cursor()
        items_count = self._fetch_value('SELECT count(*) FROM feed_content WHERE feed_id = :fid', {'fid': feed_id})
        if items_count is False:
            return False

        pages_count = math.ceil(items_count / ITEM_PER_PAGE)
        offset = int(page) * ITEM_PER_PAGE
        select_sql = 'SELECT * FROM feed_content WHERE feed_id = :fid ORDER BY pub_date DESC LIMIT ' + str(offset) + ', ' + str(ITEM_PER_PAGE)
        c.execute(select_sql, {'fid': feed_id})
        data = c.fetchall()
        return {'items': data, 'count': pages_count}

    def item_exist(self, url):
        c = self.db.cursor()
        c.execute('SELECT rowid FROM feed_content WHERE url = :u', {'u': url})
        data = c.fetchone()
        c.close()
        if data is not None and len(data) > 0:
            return True
        else:
            return False

    def exists(self, url):
        c = self.db.cursor()
        c.execute('SELECT rowid FROM feeds WHERE url = :u', {'u': url})
        data = c.fetchone()
        if data is not None and len(data) > 0:
            return data[0]
        else:
            return False

    def get_list(self):
        c = self.db.cursor()
        c.execute('SELECT rowid, name FROM feeds')
        return c.fetchall()

