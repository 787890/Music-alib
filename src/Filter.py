# -*- coding: utf-8 -*-

from src.Enums import QualityToBitrateEnums


class SongFilter:

    DEFAULT_BITRATE_RANGE = QualityToBitrateEnums
    DEFAULT_MIN_SIMILARITY = 0.5

    def __init__(self,
                 qualities=None,
                 min_similarity=DEFAULT_MIN_SIMILARITY):
        if qualities:
            self.qualities = [x.value for x in qualities]
        else:
            self.qualities = [x.value for x in self.DEFAULT_BITRATE_RANGE]
        self.min_similarity = min_similarity

    def is_meet_bitrate(self, other):
        for quality in self.qualities:
            if quality[0] <= other <= quality[1]:
                return True
        return False

    def is_meet_similarity(self, other):
        return other >= self.min_similarity
