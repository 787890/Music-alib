# -*- coding: utf-8 -*-

from functools import total_ordering
from src.Enums import QualityOrAccuracy


class Format:

    def __init__(self, format_enum):
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
class ComparableObjWithTolerance:

    def __init__(self, value, tolerance=0):
        self.value = value
        self.tolerance = tolerance

    def __eq__(self, other):
        return abs(self.value-other.value) < self.tolerance

    def __ne__(self, other):
        return not abs(self.value-other.value) < self.tolerance

    def __lt__(self, other):
        return self.value < other.value-self.tolerance

    def __gt__(self, other):
        return self.value > other.value+self.tolerance


@total_ordering
class ComparableSimilarityRatio(ComparableObjWithTolerance):

    DEFAULT_TOLERANCE = 0.15

    def __init__(self, value, tolerance=DEFAULT_TOLERANCE):
        super().__init__(value, tolerance)


@total_ordering
class ComparableBitrate(ComparableObjWithTolerance):

    DEFAULT_TOLERANCE = 50

    def __init__(self, value, tolerance=DEFAULT_TOLERANCE):
        super().__init__(value, tolerance)
        self.is_lossless = self.value > 330


class ComparableFactory:

    @staticmethod
    def get_comparable_class(item):
        if item == QualityOrAccuracy.quality_first:
            return ComparableSimilarityRatio
        if item == QualityOrAccuracy.accuracy_first:
            return ComparableBitrate
        else:
            return ComparableObjWithTolerance
