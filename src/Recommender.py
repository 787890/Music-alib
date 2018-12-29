# -*- coding: utf-8 -*-

from src.Enums import SourcePriority, FormatPriority, QualityOrAccuracy
from src.SongProperties import ComparableFactory
from src import Logger


class Recommender:

    def __init__(self,
                 format_priority=FormatPriority,
                 source_priority=SourcePriority,
                 quality_or_accuracy=QualityOrAccuracy.accuracy_first):
        self.format_priority = format_priority
        self.source_priority = source_priority
        self.first_priority_key = quality_or_accuracy

    def get_recommended(self, file_list):
        comparable_class = ComparableFactory.get_comparable_class(self.first_priority_key)
        return sorted(file_list,
                      key=lambda k: (comparable_class(k[self.first_priority_key.value]),
                                     self.source_priority.get_priority(k['ext']),
                                     self.format_priority.get_priority(k['source']))).pop()


if __name__ == '__main__':
    r = Recommender()
    l = [
        {
            "type": "ape",
            "size": 11823226,
            "size_string": "11.3 MB",
            "ext": "ape",
            "bitrate": 800,
            "bitrate_string": "800 Kbps",
            "similarity_ratio": 0.65,
            'source': 'kugou',
            "url": "http://dl.stream.qqmusic.qq.com/M800002Il7Ya1tZ6UZ.mp3?guid=7332953645&vkey=F6D16EEBE31F4622F6F2B496BA0CA1CCCC9D20E25C045103096E84E707B81DC1F3382EB1C44B27978C2C05E5862CB18C8A3B723F0B59DC68&uin=0&fromtag=53"
        },
        {
            "type": "flac",
            "size": 29249471,
            "size_string": "27.9 MB",
            "ext": "flac",
            "bitrate": 793,
            "bitrate_string": "793 Kbps",
            "similarity_ratio": 0.6,
            'source': 'kugou',
            "url": "http://dl.stream.qqmusic.qq.com/F000002Il7Ya1tZ6UZ.flac?guid=7332953645&vkey=F6D16EEBE31F4622F6F2B496BA0CA1CCCC9D20E25C045103096E84E707B81DC1F3382EB1C44B27978C2C05E5862CB18C8A3B723F0B59DC68&uin=0&fromtag=53"
        }
    ]
    res = r.get_recommended(l)
    Logger.get_logger().debug(Logger.json_format(res))
