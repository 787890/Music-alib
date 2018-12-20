# -*- coding: utf-8 -*-

import Logger
from engine.SearchEngineQq import SongSearchEngineQq
from engine.SearchEngineKugou import SongSearchEngineKugou
from Enums import Source

log = Logger.get_logger()


class SongSearchEngineFactory:

    @staticmethod
    def get_search_engine(source):
        if source == Source.QQ:
            return SongSearchEngineQq
        elif source == Source.KUGOU:
            return SongSearchEngineKugou
        else:
            # TODO: add log
            log.error("Invalid search engine. available search engines: %s" %
                      [s.name for s in Source])
