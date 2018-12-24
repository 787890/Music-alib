# -*- coding: utf-8 -*-

from enum import Enum


class RecommendPriority(Enum):
    QUALITY_FIRST = 'bitrate'
    SIMILARITY_FIRST = 'similarity_ratio'


class Source(Enum):
    QQ = 'qq'
    KUGOU = 'kugou'
