# -*- coding: utf-8 -*-

from enum import Enum


class SourceEnum(Enum):
    QQ = 'qq'
    KUGOU = 'kugou'


class FormatEnum(Enum):
    aac = 'aac'
    mp3 = 'mp3'
    flac = 'flac'
    ape = 'ape'
    wav = 'wav'

    @classmethod
    def is_lossless(cls):
        if cls.name in (cls.flac, cls.ape, cls.wav):
            return True
        else:
            return False


class QualityToBitrateEnums(Enum):
    lossless = (350, 9999)
    compress = (0, 350)


class Priority(Enum):
    default_value = 0

    @classmethod
    def get_priority(cls, key):
        if key not in cls.__members__:
            return cls.default_value.value
        return cls.__getitem__(key).value


class SourcePriority(Priority, Enum):
    KUGOU = 9
    QQ = 8


class FormatPriority(Priority, Enum):
    aac = 2
    mp3 = 3
    flac = 9
    ape = 8
    wav = 7


class QualityOrAccuracy(Enum):
    quality_first = 'bitrate'
    accuracy_first = 'similarity_ratio'
