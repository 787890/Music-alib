# -*- coding: utf-8 -*-

import Logger
from engine.SearchEngineQq import SearchEngineQq
from engine.SearchEngineKugou import SearchEngineKugou
from Enums import Source

log = Logger.get_logger()


class SearchEngineFactory:

    @staticmethod
    def get_search_engine(source):
        if source == Source.QQ:
            return SearchEngineQq
        elif source == Source.KUGOU:
            return SearchEngineKugou
        else:
            # TODO: add log
            log.error("Invalid search engine. available search engines: %s" %
                      [s.name for s in Source])
