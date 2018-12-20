# -*- coding: utf-8 -*-


class SongFilter:

    DEFAULT_MIN_BITRATE = 320
    DEFAULT_MIN_SIMILARITY = 0.5

    def __init__(self, min_bitrate=None, min_similarity=None):
        self.min_bitrate = min_bitrate or self.DEFAULT_MIN_BITRATE
        self.min_similarity = min_similarity or self.DEFAULT_MIN_SIMILARITY
