# -*- coding: utf-8 -*-

from Logger import json_format
from engine.SearchEngineBase import SearchEngineBase
import HttpRequest
from Enums import Source


class SongSearchEngineQq(SearchEngineBase):

    QQ_SEARCH_API = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
    QQ_VKEY_API = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg'
    GUID = '7332953645'

    FILE_TYPES = ['m4a', 'mp3_128', 'mp3_320', 'flac', 'ape']

    def __init__(self, query):
        super().__init__(query)
        self.search_result['source'] = Source.QQ.value

    def get_search_result(self):
        return self.search_result

    def search(self):
        min_bitrate = self.song_filter.min_bitrate if self.song_filter else 0
        min_similarity = self.song_filter.min_similarity if self.song_filter else 0
        self.log.info(
            "search source: QQ, search query: %s (bitrate >= %s, similarity ratio >= %s)" %
            (self.query_string, min_bitrate, min_similarity))

        # search for song info by query
        mid = self.__search_song_info_by_query()
        if not mid:
            return {}

        # get vkey by mid, filename, guid
        vkey, file_names = self.__get_vkey(mid)
        if not vkey:
            return {}

        # format download link
        self.__format_download_links(vkey, file_names)

        # verify download link
        self.__verify_download_links()

        if not self.search_result['files']:
            self.log.info(
                "Failed in getting download info from search source: QQ, "
                "search query: %s (bitrate >= %s, similarity ratio >= %s)" %
                (self.query_string, min_bitrate, min_similarity))

        self.log.debug(json_format(self.search_result))

    def __search_song_info_by_query(self):
        self.log.info("[QQ] search for song info")

        payload = {
            "new_json": "1",
            "t": "0",
            "aggr": "1",
            "cr": "1",
            "catZhida": "1",
            "lossless": "0",
            "flag_qc": "0",
            "p": "1",  # page
            "n": "1",  # number per page
            "w": self.query_string,  # keyword
            "format": "json",
            "inCharset": "utf8",
            "outCharset": "utf-8",
            "notice": "0",
            "platform": "yqq",
            "needNewCode": "0"
        }

        response_data = HttpRequest.request('GET', self.QQ_SEARCH_API, payload)
        self.log.debug(json_format(response_data))

        if not response_data['code'] == 0:
            self.log.info("[QQ] search api error")
            return None

        try:
            if not response_data["data"]["song"]["list"]:
                self.log.info("[QQ] Failed in finding song info")
                return None

            song = response_data["data"]["song"]["list"][0]

            # song info
            track_name = song['name']
            artists = ' '.join([x['name'] for x in song['singer']])
            mid = song['mid']

            # file info
            interval = song['interval']

            file_info = song['file']

            file_sizes = {
                'm4a': file_info['size_aac'],
                'mp3_128': file_info['size_128'],
                'mp3_320': file_info['size_320'],
                'flac': file_info['size_flac'],
                'ape': file_info['size_ape']
            }

            file_exts = {
                'm4a': 'aac',
                'mp3_128': 'mp3',
                'mp3_320': 'mp3',
                'flac': 'flac',
                'ape': 'ape'
            }

        except KeyError:
            self.log.info("[QQ] Failed in finding song info")
            return None

        self.log.info("[QQ] Found song info")

        self.search_result['track_name'] = track_name
        self.search_result['artists'] = artists
        similarity_ratio = self._get_similarity_ratio()
        min_similarity = self.song_filter.min_similarity if self.song_filter else 0
        if similarity_ratio < min_similarity:
            self.log.info("[QQ] Does not reach minimum similarity")
            return None

        if isinstance(self.query, dict):
            self.search_result['similarity_ratio'] = self._get_similarity_ratio()

        for file_type in self.FILE_TYPES:
            size = file_sizes[file_type]
            bitrate = round(file_sizes[file_type] / 1000 / interval * 8) if interval != 0 else 0
            file = {
                'type': file_type,
                'size': size,
                'size_string': self._readable_filesize(size),
                'ext': file_exts[file_type],
                'bitrate': bitrate,
                'bitrate_string': "%s kbps" % bitrate
            }
            self.search_result['files'].append(file)

        return mid

    def __get_vkey(self, mid):
        self.log.info("[QQ] get vkey by guid and filename")
        vkey = ""

        # filename prefix: C400 m4a，M500 mp3 128k，M800 mp3 320k，A100 ape, F000 Flac
        file_names = {
            'm4a': "C400%s.mp3" % mid,
            'mp3_128': "M500%s.mp3" % mid,
            'mp3_320': "M800%s.mp3" % mid,
            'flac': "F000%s.flac" % mid,
            'ape': "A100%s.ape" % mid
        }

        # TODO:Async this
        for f in self.search_result['files']:
            file_type = f['type']

            if f['size'] == 0:
                self.log.info("[QQ] skip vkey using %s" % file_type)
                continue

            self.log.info("[QQ] try vkey using %s" % file_type)
            payload = {
                "format": "json",
                "inCharset": "utf8",
                "outCharset": "utf-8",
                "notice": "0",
                "platform": "yqq",
                "needNewCode": "0",
                "cid": "205361747",
                "callback": "",
                "uin": "0",
                "songmid": mid,
                "filename": file_names[file_type],
                "guid": self.GUID
            }

            response_data = HttpRequest.request('GET', self.QQ_VKEY_API, payload=payload, is_json=True)

            if not response_data['code'] == 0:
                self.log.info("[QQ] vkey api error")
                self.log.info("[QQ] fail %s" % file_type)
                continue

            try:
                vkey = response_data['data']['items'][0]['vkey']
            except KeyError:
                self.log.info("[QQ] fail vkey using%s" % file_type)
                continue

            if not vkey:
                self.log.info("[QQ] fail vkey using%s" % file_type)
                continue
            else:
                self.log.info("[QQ] Succesfully got vkey")
                break

        if not vkey:
            self.log.info("[QQ] Failed in getting vkey")
            return None, None

        return vkey, file_names

    def __format_download_links(self, vkey, file_names):
        for f in self.search_result['files']:
            file_type = f['type']
            # filtered by minimum bitrate
            min_bitrate = self.song_filter.min_bitrate if self.song_filter else 0
            if f['bitrate'] < min_bitrate:
                self.search_result['files'].remove(f)
                continue

            f['url'] = "http://dl.stream.qqmusic.qq.com/%s?guid=%s&vkey=%s&uin=0&fromtag=53" % (
                file_names[file_type], self.GUID, vkey)

    def __verify_download_links(self):
        for f in self.search_result['files']:
            file_type = f['type']
            response_data = HttpRequest.request('GET', f['url'], is_json=False)
            if response_data != 200:
                self.log.info("[QQ] Failed in verify download link %s" % file_type)
                self.search_result['files'].remove(f)


if __name__ == '__main__':
    query = {"track_name": "Hello", "artists": "Adele"}
    s = SongSearchEngineQq(query)
    s.search()
    r = s.get_search_result()
