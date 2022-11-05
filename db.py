import psycopg2
import json
import datetime
import time
import logging
from loguru import logger

logger.add(
    "autoganjlogs",
    format="{time} {level} {message}",
    level="INFO",
    rotation="1 day",
    retention="7 days",
    compression="zip",
)

class DB:

    def __init__(self, config_file):
        self.config_file = config_file
        self.conn = None
        self.cur = None        
        
    def connect(self):
        try:
            with open(self.config_file) as f:
                config = json.load(f)['db_creds']
                self.conn = psycopg2.connect("dbname='{}' user='{}' host='localhost' password='{}'".format(
                    config['dbname'], config['user'], config['pass']))
                self.cur = self.conn.cursor()
        except Exception as e:
            logger.exception('Error connecting to db: {}'.format(e))

    def disconnect(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception as e:
            logger.exception('Error disconnecting from db: {}'.format(e))

    def get_all_news_tables(self):
        try:
            query = "SELECT table_name FROM information_schema.tables where table_type='BASE TABLE' AND table_schema='public' AND table_name like 'news_articles_%'"
            self.cur.execute(query)
            tables = self.cur.fetchall()
            self.conn.commit()
            return tables
        except Exception as e:
            logger.exception('Error getting news tables: {}'.format(e))
            logger.exception(e)

    def get_articles(self, date=None, fields = None, search_filter = {}):
        self.connect()
        if fields is None:
            fields = "*"

        try:
            articles = []
            if date is None:
                for table in self.get_all_news_tables():
                    if len(search_filter):
                        where_clause = self.build_query_string(date, search_filter)
                        #logger.info(where_clause)
                        query = f"SELECT {fields} FROM {table[0]} WHERE {where_clause}"
                    else:
                        query = f"SELECT {fields} FROM {table[0]}"
                    #logger.info([fields, query])    
                    self.cur.execute(query)
                    articles.append(self.cur.fetchall())
                    self.conn.commit()
            else:
                    if len(search_filter):
                        query = f"SELECT {fields} FROM news_articles_{date} WHERE " + self.build_query_string(date, search_filter)
                    else:
                        query = f"SELECT {fields} FROM news_articles_{date}"                
                    #logger.info(query)
                    self.cur.execute(query)
                    articles.append(self.cur.fetchall())
                    self.conn.commit()
            
            self.disconnect()
            return articles

        except Exception as e:
            logger.exception('Error getting articles: {}'.format(e))

    def build_query_string(self, date, search_filter):
        query_string = ''
        for key, value in search_filter.items():
            if key == 'AND':
                query_string += self.build_and_query(date, value)
            elif key == 'OR':
                query_string += self.build_or_query(date, value)
            elif key == 'BETWEEN':
                query_string += self.build_between_query(date, value)
        return query_string

    def build_and_query(self, date, search_filter):
        query = ''
        for key, value in search_filter.items():
            if type(value) is list:
                query += "keywords @> ARRAY[{}] AND ".format(
                    ','.join([str(x) for x in value]))
            else:
                query += "{} ILIKE '%{}%' AND ".format(key, value)
        return query[:-4]

    def build_or_query(self, date, search_filter):
        query = ''
        for key, value in search_filter.items():
            if type(value) is list:
                query += "keywords @> ARRAY[{}] OR ".format(
                    ','.join([str(x) for x in value]))
            else:
                query += "{} ILIKE '%{}%' AND ".format(key, value)
        return query[:-3]

    def build_between_query(self, date, search_filter):
        query = ''
        for key, value in search_filter.items():
            query += "{} BETWEEN '{}' AND '{}'".format(key, value[0], value[1])
        return query

    def get_trending_keywords_for_date_range(self, start_date=None, end_date=None, news_source=None, country=None, language=None):
        """Get a list of keywords and their frequency for a given date range."""
        try:
            if start_date is None:
                start_date = datetime.datetime.now() - datetime.timedelta(days=7)
            if end_date is None:
                end_date = datetime.datetime.now()
            if news_source is None:
                news_source = '%'
            if country is None:
                country = '%'
            if language is None:
                language = '%'

            query = "SELECT keywords, COUNT(*) FROM news_articles_{} WHERE date_published BETWEEN '{}' AND '{}' AND news_source LIKE '{}' AND country_name LIKE '{}' AND language LIKE '{}' GROUP BY keywords ORDER BY COUNT(*) DESC".format(
                start_date.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), news_source, country, language)
            self.cur.execute(query)
            keywords = self.cur.fetchall()
            return keywords
        except Exception as e:
            logger.exception('Error getting trending keywords: {}'.format(e))

    def get_distinct_languages(self):
        # Get a unique list of languages from all news_ddmmyyyy tables.
        try:
            query = "SELECT DISTINCT language FROM news_articles_*"
            self.cur.execute(query)
            languages = self.cur.fetchall()
            return languages
        except Exception as e:
            logger.exception('Error getting distinct languages: {}'.format(e))

    def get_distinct_countries(self):
        # Get a unique list of countries from all news_ddmmyyyy tables.
        try:
            query = "SELECT DISTINCT country_name FROM news_articles_*"
            self.cur.execute(query)
            countries = self.cur.fetchall()
            return countries
        except Exception as e:
            logger.exception('Error getting distinct countries: {}'.format(e))

    def get_distinct_news_sources(self):
        # Get a unique list of news sources from all news_ddmmyyyy tables.
        try:
            query = "SELECT DISTINCT news_source FROM news_articles_*"
            self.cur.execute(query)
            news_sources = self.cur.fetchall()
            return news_sources
        except Exception as e:
            logger.exception('Error getting distinct news sources: {}'.format(e))

    def get_distinct_keywords(self):
        # Get a unique list of keywords from all news_ddmmyyyy tables.
        try:
            query = "SELECT DISTINCT keywords FROM news_articles_*"
            self.cur.execute(query)
            keywords = self.cur.fetchall()
            return keywords
        except Exception as e:
            logger.exception('Error getting distinct keywords: {}'.format(e))

    def get_distinct_authors(self):
        # Get a unique list of authors from all news_ddmmyyyy tables.
        try:
            query = "SELECT DISTINCT authors FROM news_articles_*"
            self.cur.execute(query)
            authors = self.cur.fetchall()
            return authors
        except Exception as e:
            logger.exception('Error getting distinct authors: {}'.format(e))

    def get_distinct_date_published(self):
        # Get a unique list of dates from all news_ddmmyyyy tables.
        try:
            query = "SELECT DISTINCT date_published FROM news_articles_*"
            self.cur.execute(query)
            dates = self.cur.fetchall()
            return dates
        except Exception as e:
            logger.exception('Error getting distinct dates: {}'.format(e))

    def get_distinct_date_updated(self):
        # Get a unique list of dates from all news_ddmmyyyy tables.
        try:
            query = "SELECT DISTINCT date_updated FROM news_articles_*"
            self.cur.execute(query)
            dates = self.cur.fetchall()
            return dates
        except Exception as e:
            logger.exception('Error getting distinct dates: {}'.format(e))

    def get_distinct_date_downloaded(self):
        # Get a unique list of dates from all news_ddmmyyyy tables.
        try:
            query = "SELECT DISTINCT date_downloaded FROM news_articles_*"
            self.cur.execute(query)
            dates = self.cur.fetchall()
            return dates
        except Exception as e:
            logger.exception('Error getting distinct dates: {}'.format(e))

    def get_distinct_titles_by_language(self, language=None):
        # Get a unique list of titles from all news_ddmmyyyy tables.
        try:
            if language is None:
                query = "SELECT DISTINCT title FROM news_articles_*"
            else:
                query = "SELECT DISTINCT title FROM news_articles_* WHERE language = '{}'".format(
                    language)
            self.cur.execute(query)
            titles = self.cur.fetchall()
            return titles
        except Exception as e:
            logger.exception('Error getting distinct titles: {}'.format(e))

    def get_distinct_titles_by_country(self, country=None):
        # Get a unique list of titles from all news_ddmmyyyy tables.
        try:
            if country is None:
                query = "SELECT DISTINCT title FROM news_articles_*"
            else:
                query = "SELECT DISTINCT title FROM news_articles_* WHERE country_name = '{}'".format(
                    country)
            self.cur.execute(query)
            titles = self.cur.fetchall()
            return titles
        except Exception as e:
            logger.exception('Error getting distinct titles: {}'.format(e))

    def get_distinct_titles_by_news_source(self, news_source=None):
        # Get a unique list of titles from all news_ddmmyyyy tables.
        try:
            if news_source is None:
                query = "SELECT DISTINCT title FROM news_articles_*"
            else:
                query = "SELECT DISTINCT title FROM news_articles_* WHERE news_source = '{}'".format(
                    news_source)
            self.cur.execute(query)
            titles = self.cur.fetchall()
            return titles
        except Exception as e:
            logger.exception('Error getting distinct titles: {}'.format(e))

    def get_distinct_titles_by_keyword(self, keyword=None):
        # Get a unique list of titles from all news_ddmmyyyy tables.
        try:
            if keyword is None:
                query = "SELECT DISTINCT title FROM news_articles_*"
            else:
                query = "SELECT DISTINCT title FROM news_articles_* WHERE keywords @> ARRAY[{}]".format(
                    keyword)
            self.cur.execute(query)
            titles = self.cur.fetchall()
            return titles
        except Exception as e:
            logger.exception('Error getting distinct titles: {}'.format(e))

        
    def get_top_trending_articles_by_keywords_per_hour_last_n_days(self, n_days=3):
        try:
            # Get the top 10 keywords for each hour over the last N days.
            tables = self.get_all_news_tables()
            keywords = {}
            for table in tables:
                query = f"SELECT DATE_TRUNC('hour', date_downloaded) as hour, UNNEST(keywords) as keyword, COUNT(*) FROM {table[0]} GROUP BY hour, keyword ORDER BY hour DESC LIMIT {n_days * 24}"
                self.cur.execute(query)
                result = self.cur.fetchall()

                # Build a dictionary of keywords per hour with the count of articles downloaded that contain that keyword in that hour.
                for row in result:
                    if row[0] not in keywords:
                        keywords[row[0]] = {}

                    if row[1] not in keywords[row[0]]:                        
                        keywords[row[0]][row[1]] = 0

                    keywords[row[0]][row[1]] += 1

            # Get the top 10 trending keywords per hour over the last N days and build a list of these 20 trending terms to search for articles downloaded in the last 15 minutes that contain these terms.            
            trending_keywords = []
            for hour in keywords:
                trending_keywords.append(sorted(keywords[hour], key=keywords[hour].get, reverse=True)[:10])

            # Flatten the list of lists of trending keywords into a single list.
            trending_keywords = [item for sublist in trending_keywords for item in sublist]

            # Get the articles downloaded in the last 15 minutes that contain any of the top 20 trending keywords.
            query = f"SELECT * FROM news_articles_{datetime.datetime.now().strftime('%d%m%Y')} WHERE date_downloaded > NOW() - INTERVAL '15 minutes' AND keywords && ARRAY[{','.join([str(x) for x in trending_keywords])}] LIMIT 20"
            self.cur.execute(query)
            result = self.cur.fetchall()
            

        except Exception as e:
            logger.exception('Error getting top 10 trending keywords per hour over the last {} days: {}'.format(n_days, e))
            
        return result

if __name__ == "__main__":
    print("Checking if DB is setup for News Scanner.")
    db = DB("config.json")
    db.connect()
    news = db.get_top_trending_articles_by_keywords_per_hour_last_n_days()
    for n in news:
        print(n[15])
    db.disconnect()
    print("Finished.")
