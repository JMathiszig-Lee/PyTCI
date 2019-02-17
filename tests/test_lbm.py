import pytest
from PyTCI.weights import leanbodymass


def test_james():
    assert round(leanbodymass.james(165, 90, "f")) == 52
    assert round(leanbodymass.james(180, 60, "m")) == 52

    with pytest.raises(ValueError):
        leanbodymass.james(180, 60, "g")


def test_bmi():
    assert leanbodymass.bmi(180, 60) == 18.5


def test_boer():
    assert leanbodymass.boer(180, 60, "m") == 53.3
    assert leanbodymass.boer(165, 90, "f") == 52.4

    with pytest.raises(ValueError):
        leanbodymass.boer(180, 60, "g")


def test_hume66():
    assert leanbodymass.hume66(180, 60, "m") == 51.2
    assert leanbodymass.hume66(165, 90, "f") == 52.3

    with pytest.raises(ValueError):
        leanbodymass.hume66(180, 60, "g")


def test_hume71():
    assert leanbodymass.hume71(180, 60, "m") == 53.2
    assert leanbodymass.hume71(165, 90, "f") == 52.2

    with pytest.raises(ValueError):
        leanbodymass.hume71(180, 60, "g")


def test_janmahasation():
    assert leanbodymass.janmahasation(180, 60, "m") == 52.1
    assert leanbodymass.janmahasation(165, 90, "f") == 49.5

    with pytest.raises(ValueError):
        leanbodymass.janmahasation(180, 60, "g")


def test_idealbodyweight():
    assert leanbodymass.idealbodyweight(180, 'm') == 75.1
    assert leanbodymass.idealbodyweight(165, "f") == 57.0

    with pytest.raises(ValueError):
        leanbodymass.idealbodyweight(180, "g")

def test_adjustedbodyweight():
    assert leanbodymass.adjustedbodyweight(180, 80, "m") == 77.1
    assert leanbodymass.adjustedbodyweight(165, 90, "f") == 70.2

    with pytest.raises(ValueError):
        leanbodymass.adjustedbodyweight(180, 60, "g")