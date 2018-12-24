# -*- coding: utf-8 -*-


class SongFilter:

    DEFAULT_MIN_BITRATE = 320
    DEFAULT_MIN_SIMILARITY = 0.5

    def __init__(self, min_bitrate=DEFAULT_MIN_BITRATE, min_similarity=DEFAULT_MIN_SIMILARITY):
        self.min_bitrate = min_bitrate
        self.min_similarity = min_similarity
