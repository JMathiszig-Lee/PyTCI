from PyTCI.models import propofol
#source for values independantly derived https://academic.oup.com/view-large/91165989

def test_schnider():
    testpatient = propofol.Schnider(40, 70, 170, 'm')
    assert round(testpatient.v2) == 24
    # assert testpatient.k10 == (0.384 /60)
    # assert testpatient.k12 == 0.375
    # assert testpatient.k21== 0.067

    testpatient.give_drug(200)
    assert round(testpatient.x1, 2) == 46.84

def test_marsh():
    testpatient = propofol.Marsh(70)

    assert round(testpatient.v1, 1) == 16.0
    assert round(testpatient.v2, 1) == 32.4
    assert round(testpatient.v3, 1) == 202.5
