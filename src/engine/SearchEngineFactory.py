# -*- coding: utf-8 -*-

from src import Logger
from src.engine.SearchEngineQq import SearchEngineQq
from src.engine.SearchEngineKugou import SearchEngineKugou
from src.Enums import SourceEnum

log = Logger.get_logger()


class SearchEngineFactory:

    @staticmethod
    def get_search_engine(source):
        if source == SourceEnum.QQ:
            return SearchEngineQq
        elif source == SourceEnum.KUGOU:
            return SearchEngineKugou
        else:
            log.error("Invalid search engine. available search engines: %s" %
                      [s.name for s in SourceEnum])
