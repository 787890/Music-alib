# -*- coding: utf-8 -*-

from enum import Enum


class RecommendPriority(Enum):
    QUALITY_FIRST = 'bitrate'
    SIMILARITY_FIRST = 'similarity_ratio'


class Source(Enum):
    QQ = 'qq'
    KUGOU = 'kugou'


# ExtPriority rule: flac > ape > others
class ExtPriority(Enum):
    flac = 9
    ape = 8
    default_value = 0

    @classmethod
    def get_value(cls, ext):
        if ext not in cls.__members__:
            return cls.default_value.value
        return cls.__getitem__(ext).value


# sourcePriority rule: kugou > qq > others
class SourcePriority(Enum):
    kugou = 9
    qq = 8
    default_value = 0

    @classmethod
    def get_value(cls, source):
        if source not in cls.__members__:
            return cls.default_value.value
        return cls.__getitem__(source).value
