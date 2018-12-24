# -*- coding: utf-8 -*-

from difflib import SequenceMatcher

from src import Logger


class SearchEngineBase:

    def __init__(self, query, song_filter=None):
        self.query = query
        self.query_string = "%s %s" % (query['track_name'], query['artists']) if isinstance(query, dict) else query
        self.song_filter = song_filter
        self.log = Logger.get_logger()
        self.search_result = {
            'query': self.query_string,
            'track_name': None,
            'artists': None,
            'similarity_ratio': None,
            'source': None,
            'files': []
        }

    def set_query(self, query):
        self.search_result['query'] = query
        self.search_result['query_string'] = \
            "%s %s" % (query['song_name'], query['artists']) if isinstance(query, dict) else query

    # TODO: need to find a more percise algorithm
    def _get_similarity_ratio(self):
        o_name = str.strip(str.lower(self.query['track_name']))
        o_art = str.strip(str.lower(self.query['artists']))
        a_name = str.strip(str.lower(self.search_result['track_name']))
        a_art = str.strip(str.lower(self.search_result['artists']))

        name_ratio = SequenceMatcher(None, o_name, a_name).ratio()
        artist_ratio = SequenceMatcher(None, o_art, a_art).ratio()

        return name_ratio * artist_ratio

    def _readable_filesize(self, num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'T', suffix)


if __name__ == "__main__":
    n1 = '裏表ラバーズ'
    a1 = 'wowaka 初音ミク'
    n2 = '裏表ラバーズ'
    a2 = '初音ミク、wowaka'
