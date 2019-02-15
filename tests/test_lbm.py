from ..weights import leanbodymass


def test_james():
    assert round(leanbodymass.james(165, 90, "f")) == 52
    assert round(leanbodymass.james(180, 60, "m")) == 52


def test_bmi():
    assert leanbodymass.bmi(180, 60) == 18.5


def test_boer():
    assert leanbodymass.boer(180, 60, "m") == 53.3


def test_hume66():
    assert leanbodymass.hume66(180, 60, "m") == 51.2


def test_hume71():
    pass


def test_janmahasation():
    assert leanbodymass.janmahasation(180, 60, "m") == 52.1
    assert leanbodymass.janmahasation(165, 90, "f") == 49.5
