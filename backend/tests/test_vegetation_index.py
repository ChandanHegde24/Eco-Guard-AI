import pytest

import data_layer.ai_layer.vegetation_index as vegetation_index
from data_layer.ai_layer.vegetation_index import analyze_environmental_change


class FakeRegionValue:
    def __init__(self, value: float):
        self.value = value

    def getInfo(self):
        return self.value


class FakeRegionResult:
    def __init__(self, value: float):
        self.value = value

    def get(self, _name: str):
        return FakeRegionValue(self.value)


class FakeChangeImage:
    def __init__(self, value: float):
        self.value = value

    def rename(self, _name: str):
        return self

    def reduceRegion(self, **_kwargs):
        return FakeRegionResult(self.value)


class FakeIndexedImage:
    def __init__(self, index_value: float):
        self.index_value = index_value

    def select(self, _name: str):
        return self

    def subtract(self, other: "FakeIndexedImage"):
        return FakeChangeImage(self.index_value - other.index_value)


class FakeBand:
    def __init__(self, value: float):
        self.value = value

    def rename(self, _name: str):
        return self


class FakeImage:
    def __init__(self, index_value: float):
        self.index_value = index_value

    def normalizedDifference(self, _bands):
        return FakeBand(self.index_value)

    def addBands(self, band: FakeBand):
        return FakeIndexedImage(band.value)

    def geometry(self):
        return "fake-geometry"


class FakeReducer:
    @staticmethod
    def mean():
        return "mean"


class FakeEE:
    Reducer = FakeReducer


def test_environmental_change_computes_percentage(monkeypatch) -> None:
    monkeypatch.setattr(vegetation_index, "ee", FakeEE)
    t1 = FakeImage(0.20)
    t2 = FakeImage(0.08)

    change = analyze_environmental_change(t1, t2, index_type="NDVI")

    assert change == pytest.approx(12.0)


def test_environmental_change_rejects_invalid_index_type() -> None:
    t1 = FakeImage(0.1)
    t2 = FakeImage(0.2)

    with pytest.raises(ValueError, match="Invalid index_type"):
        analyze_environmental_change(t1, t2, index_type="INVALID")
