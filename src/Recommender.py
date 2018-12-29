# -*- coding: utf-8 -*-

from src.Enums import SourcePriority, FormatPriority, QualityOrAccuracy


class Recommender:

    def __init__(self,
                 format_priority=FormatPriority,
                 source_priority=SourcePriority,
                 quality_or_accuracy=QualityOrAccuracy.accuracy_first):
        self.format_priority = format_priority
        self.source_priority = source_priority
        self.fist_priority_key = quality_or_accuracy

    def get_recommended(self, file_list):
        return sorted(file_list,
                      key=lambda k: (k[self.fist_priority_key.value],
                                     self.source_priority.get_priority(k['ext']),
                                     self.format_priority.get_priority(k['source']))).pop()
