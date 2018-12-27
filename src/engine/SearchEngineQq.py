# -*- coding: utf-8 -*-

import asyncio
import json

from src.Filter import SongFilter
from src.Logger import json_format
from src.engine.SearchEngineBase import SearchEngineBase
from src import HttpRequest
from src.Enums import Source


class SearchEngineQq(SearchEngineBase):

    QQ_SEARCH_API = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
    QQ_VKEY_API = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg'
    GUID = '7332953645'

    SOURCE_NAME = Source.QQ.value

    FILE_TYPES = ['m4a', 'mp3_128', 'mp3_320', 'flac', 'ape']

    FILE_SIZE_KEY_MAPPING = {
        'm4a': 'size_aac',
        'mp3_128': 'size_128',
        'mp3_320': 'size_320',
        'flac': 'size_flac',
        'ape': 'size_ape'
    }

    FILE_EXTS_MAPPING = {
        'm4a': 'aac',
        'mp3_128': 'mp3',
        'mp3_320': 'mp3',
        'flac': 'flac',
        'ape': 'ape'
    }

    # filename prefix: C400 m4a，M500 mp3 128k，M800 mp3 320k，A100 ape, F000 Flac
    FILE_NAMES_PREFIX_MAPPING = {
        'm4a': 'C400',
        'mp3_128': 'M500',
        'mp3_320': 'M800',
        'flac': 'F000',
        'ape': 'A100'
    }

    def __init__(self, query, song_filter=None):
        super().__init__(query, song_filter)
        self.search_result['source'] = self.SOURCE_NAME
        self.vkey = None
        self.file_names = None

    def get_search_result(self):
        return self.search_result

    async def search(self):
        min_bitrate = self.song_filter.min_bitrate if self.song_filter else 0
        min_similarity = self.song_filter.min_similarity if self.song_filter else 0
        self.log.info(
            "Start searching. source: QQ, query: %s (bitrate >= %s, similarity ratio >= %s)" %
            (self.query_string, min_bitrate, min_similarity))

        # search for song info by query
        mid = self.__search_song_info_by_query()

        # get vkey by mid, filename, guid
        await self.__get_vkey(mid)

        # format and validate download link by vkey, file_name
        self.__format_download_links()

        self.log.debug(json_format(self.search_result))

        if not self.search_result['files']:
            self.log.info(
                "Failed in finding download info from search source: QQ, "
                "search query: %s (bitrate >= %s, similarity ratio >= %s)" %
                (self.query_string, min_bitrate, min_similarity))
            return

        self.log.info(
            "Succeeded in finding download info from search source: QQ, "
            "search query: %s (bitrate >= %s, similarity ratio >= %s)" %
            (self.query_string, min_bitrate, min_similarity))

    def __search_song_info_by_query(self):
        if self.query_string == '':
            return

        self.log.debug("[QQ] [song_info] start searching for song info")

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

        try:
            if not response_data['code'] == 0:
                self.log.debug("[QQ] [song_info] search api return error")
                return None

            if not response_data["data"]["song"]["list"]:
                self.log.debug("[QQ] [song_info] Failed in finding song info, due to empty file list")
                return None

            song = response_data["data"]["song"]["list"][0]

            # song info
            self.search_result['track_name'] = song['name']
            self.search_result['artists'] = ' '.join([x['name'] for x in song['singer']])
            mid = song['mid']

            # file info
            interval = song['interval']

            file_info = song['file']

            for file_type in self.FILE_TYPES:
                size = file_info[self.FILE_SIZE_KEY_MAPPING[file_type]]
                bitrate = round(size/1000/interval*8) if interval != 0 else 0
                ext = self.FILE_EXTS_MAPPING[file_type]
                file = {
                    'type': file_type,
                    'size': size,
                    'size_string': self._readable_filesize(size),
                    'ext': ext,
                    'bitrate': bitrate,
                    'bitrate_string': "%d Kbps" % bitrate
                }
                self.search_result['files'].append(file)

        except KeyError:
            self.log.debug("[QQ] [song_info] Failed in finding song info, due to unexpected json key")
            return None

        self.log.debug("[QQ] [song_info] Succeeded in finding song info")

        if isinstance(self.query, dict):
            similarity_ratio = self._get_similarity_ratio()
            min_similarity = self.song_filter.min_similarity if self.song_filter else 0

            self.search_result['similarity_ratio'] = similarity_ratio

            if similarity_ratio < min_similarity:
                self.log.debug(
                    "[QQ] [song_info] Discard all result, not meeting minimun similarity ratio: %s" % min_similarity)
                return None

        return mid

    async def __get_vkey(self, mid):
        if not mid:
            return None, None

        self.log.debug("[QQ] [vkey] start requesting for vkey by guid and filename")
        vkey = ""

        file_names = {}
        for t in self.FILE_TYPES:
            prefix = self.FILE_NAMES_PREFIX_MAPPING[t]
            ext = self.FILE_EXTS_MAPPING[t]
            file_names[t] = "%s%s.%s" % (prefix, mid, ext)

        tasks = [HttpRequest.async_request(
            'GET',
            self.QQ_VKEY_API, {
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
                "filename": file_names[f['type']],
                "guid": self.GUID
            },
            file_type=f['type']
        ) for f in self.search_result['files']]

        responses = await asyncio.gather(*tasks)

        for response in responses:
            response_data = json.loads(response[0])
            file_type = response[1]['file_type']

            self.log.debug("checking type %s" % file_type)

            if not response_data['code'] == 0:
                self.log.debug("[QQ] [vkey] failed type %s, due to api return error" % file_type)
                continue

            try:
                vkey = response_data['data']['items'][0]['vkey']
            except KeyError:
                self.log.debug("[QQ] [vkey] failed type %s, due to unexpected json key" % file_type)
                continue

            if not vkey:
                self.log.debug("[QQ] [vkey] failed type %s, due to empty vkey value" % file_type)
                continue
            else:
                self.log.debug("[QQ] [vkey] Succeeded in getting vkey")
                break

        if not vkey:
            self.log.debug("[QQ] [vkey] Failed in getting vkey by all types")
            return None, None

        self.vkey = vkey
        self.file_names = file_names

    def __format_download_links(self):

        def __is_valid_download_link__(file):
            if not self.vkey or not self.file_names:
                return False

            file_type = file['type']
            if file['size'] == 0:
                self.log.debug("[QQ] [link] Discard type: %s, due to invalid file size: %s" % (file_type, file['size']))
                return False

            min_bitrate = self.song_filter.min_bitrate if self.song_filter else 0

            if file['bitrate'] < min_bitrate:
                self.log.debug(
                    "[QQ] [link] Discard type: %s, not meeting minimal bitrate: %s" % (file_type, min_bitrate))
                return False

            file_name = self.file_names[file_type]
            url = "http://dl.stream.qqmusic.qq.com/%s?guid=%s&vkey=%s&uin=0&fromtag=53" % (
                file_name, self.GUID, self.vkey)

            # TODO: qq api returns 403 with all HEAD method, need to find another method to validate
            # if not HttpRequest.validate_download_url(url):
            #     self.log.debug("[QQ] [link] Failed in verify download link %s" % file_type)
            #     return False

            file['url'] = url
            self.log.debug("[QQ] [link] Succeeded in verify download link %s" % file_type)
            return True

        self.search_result['files'] = [f for f in self.search_result['files'] if __is_valid_download_link__(f)]


if __name__ == '__main__':
    query = {"track_name": "Orion", "artists": "米津玄師"}
    fltr = SongFilter(min_bitrate=0)
    s = SearchEngineQq(query, fltr)
    s.search()
    r = s.get_search_result()
