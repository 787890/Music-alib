# -*- coding: utf-8 -*-

from src import Logger
from src.engine.SearchEngineQq import SearchEngineQq
from src.engine.SearchEngineKugou import SearchEngineKugou
from src.Enums import Source

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
