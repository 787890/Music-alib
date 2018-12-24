# -*- coding: utf-8 -*-

from hashlib import md5

from src.engine.SearchEngineBase import SearchEngineBase
from src import HttpRequest
from src.Logger import json_format
from src.Enums import Source
from src.Filter import SongFilter


class SearchEngineKugou(SearchEngineBase):

    KUGOU_MUSIC_SEARCH_API = "http://songsearch.kugou.com/song_search_v2"
    KUGOU_MUSIC_DOWNLOAD_API = "http://trackercdnbj.kugou.com/i/v2/"

    SOURCE_NAME = Source.KUGOU.value

    FILE_TYPES = ['compressed', 'lossless']

    FILE_SIZE_KEY_MAPPING = {
        'compressed': 'HQFileSize',
        'lossless': 'SQFileSize',
    }

    FILE_BITRATE_KEY_MAPPING = {
        'compressed': 'HQBitrate',
        'lossless': 'SQBitrate',
    }

    FILE_HASH_KEY_MAPPING = {
        'compressed': 'HQFileHash',
        'lossless': 'SQFileHash',
    }

    def __init__(self, query, song_filter=None):
        super().__init__(query, song_filter)
        self.search_result['source'] = self.SOURCE_NAME

    def get_search_result(self):
        return self.search_result

    def search(self):
        min_bitrate = self.song_filter.min_bitrate if self.song_filter else 0
        min_similarity = self.song_filter.min_similarity if self.song_filter else 0
        self.log.info(
            "search source: KUGOU, search query: %s (bitrate >= %s, similarity ratio >= %s)" %
            (self.query_string, min_bitrate, min_similarity))

        # search for song info by query
        self.__search_song_info_by_query()

        self.log.debug(json_format(self.search_result))

        if not self.search_result['files']:
            self.log.info(
                "Failed in getting download info from search source: Kugou, "
                "search query: %s (bitrate >= %s, similarity ratio >= %s)" %
                (self.query_string, min_bitrate, min_similarity))

        self.log.info(
            "Succeeded in finding download info from search source: Kugou, "
            "search query: %s (bitrate >= %s, similarity ratio >= %s)" %
            (self.query_string, min_bitrate, min_similarity))

        self.log.debug(json_format(self.search_result))

    def __search_song_info_by_query(self):
        if self.query_string == '':
            return

        self.log.debug("[KUGOU] [song_info] start searching for song info")
        payload = {'keyword': self.query_string}
        response_data = HttpRequest.request('GET', self.KUGOU_MUSIC_SEARCH_API, payload)

        if not response_data["error_code"] == 0:
            self.log.debug("[KUGOU] [song_info] search api return error")
            return

        min_bitrate = self.song_filter.min_bitrate if self.song_filter else 0

        try:
            song_info = response_data["data"]["lists"][0]

            self.log.debug(json_format(song_info))

            self.log.debug("[KUGOU] [song_info] Successfully found song info")

            # song info
            self.search_result['track_name'] = song_info['SongName']
            self.search_result['artists'] = song_info['SingerName']

            if isinstance(self.query, dict):
                similarity_ratio = self._get_similarity_ratio()
                min_similarity = self.song_filter.min_similarity if self.song_filter else 0

                self.search_result['similarity_ratio'] = similarity_ratio

                if similarity_ratio < min_similarity:
                    self.log.debug(
                        "[KUGOU] [song_info] All files are discarded, not meeting minimum similarity: %s"
                        % min_similarity)
                    return

            # file info
            for file_type in self.FILE_TYPES:
                size = song_info[self.FILE_SIZE_KEY_MAPPING[file_type]]
                bitrate = song_info[self.FILE_BITRATE_KEY_MAPPING[file_type]]

                if size == 0:
                    self.log.debug(
                        "[KUGOU] [song_info] Discard file type: %s, due to invalid file size" % file_type)
                    continue

                if bitrate < min_bitrate:
                    self.log.debug(
                        "[KUGOU] [song_info] Discard file type: %s, not meeting minimum bitrate" % file_type)
                    continue

                # hash
                hash_str = song_info[self.FILE_HASH_KEY_MAPPING[file_type]]

                url, ext = self.__get_download_links(hash_str, file_type)

                if not url or not ext:
                    continue

                if not HttpRequest.validate_download_url(url):
                    self.log.debug("[KUGOU] [song_info] Discard file type: %s, due to invalid url" % file_type)
                    continue

                file = {
                    'type': file_type,
                    'url': url,
                    'ext': ext,
                    'size': size,
                    'size_string': self._readable_filesize(size),
                    'bitrate': bitrate,
                    'bitrate_string': "%s Kbps" % bitrate
                }
                self.search_result['files'].append(file)

        except KeyError:
            self.log.debug("[KUGOU] [song_info] Failed in finding song info, due to unexpected json key")
            return

        if not self.search_result['files']:
            self.log.debug("[KUGOU] [song_info] Failed in finding song info, due to empty result")
            return

    def __get_download_links(self, hash_str, file_type):
        h_str = str.lower(hash_str)
        key = self.__md5_kugouv2(h_str)

        payload = {
            "cmd": "23",
            "pid": "1",
            "behavior": "download",
            "hash": h_str,
            "key": key
        }

        response_data = HttpRequest.request('GET', self.KUGOU_MUSIC_DOWNLOAD_API, payload)

        try:
            if not (("status" in response_data) and (response_data["status"] == 1 and response_data["url"])):
                self.log.debug("[KUGOU] [link] Failed in getting download link for type: %s" % file_type)
                return None, None

            url = response_data['url']
            ext = response_data['extName']

        except KeyError:
            self.log.debug("[KUGOU] [link] Failed in getting download link for type: %s" % file_type)
            return None, None

        self.log.debug("[KUGOU] [link] Succeeded in getting download link for type: %s" % file_type)

        return url, ext

    # key is required for getting download link, key = md5(hash + 'kgcloudv2')
    @staticmethod
    def __md5_kugouv2(hash_string):
        return md5((hash_string + 'kgcloudv2').encode('utf-8')).hexdigest()


if __name__ == '__main__':
    query = {"track_name": "打上花火", "artists": "米津玄師"}
    fltr = SongFilter()
    s = SearchEngineKugou(query, fltr)
    s.search()
    r = s.get_search_result()
