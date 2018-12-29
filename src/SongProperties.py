# -*- coding: utf-8 -*-

from functools import total_ordering

from src.Enums import FormatEnum


class Format:

    def __init__(self, format_enum: FormatEnum):
        self.format = format_enum
        self.ext = ".%s" % format_enum.value
        self.is_lossless = format_enum.is_lossless()

    def get_ext(self):
        return self.ext

    def get_is_lossless(self):
        return self.is_lossless

    def get_format_value(self):
        return self.format.value


@total_ordering
class SimilarityRatio:

    TOLERANCE = 0.15

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return abs(self.value-other.value) < self.TOLERANCE

    def __ne__(self, other):
        return not abs(self.value-other.value) < self.TOLERANCE

    def __lt__(self, other):
        return self.value < other.value-self.TOLERANCE

    def __gt__(self, other):
        return self.value > other.value+self.TOLERANCE


@total_ordering
class Bitrate:

    TOLERANCE = 50

    def __init__(self, value):
        self.value = value
        self.is_lossless = self.value > 330

    def __eq__(self, other):
        return abs(self.value-other.value) < self.TOLERANCE

    def __ne__(self, other):
        return not abs(self.value-other.value) < self.TOLERANCE

    def __lt__(self, other):
        return self.value < other.value-self.TOLERANCE

    def __gt__(self, other):
        return self.value > other.value+self.TOLERANCE
