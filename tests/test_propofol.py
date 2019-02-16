from ..models import propofol

def test_schnider():
    testpatient = propofol.Schnider(40, 70, 170, 'm')
    assert round(testpatient.v2) == 24
    # assert testpatient.k10 == (0.384 /60)
    # assert testpatient.k12 == 0.375
    # assert testpatient.k21== 0.067

    testpatient.give_drug(200)
    assert round(testpatient.x1, 2) == 46.84
