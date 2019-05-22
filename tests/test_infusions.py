from PyTCI.models import propofol

def test_reset():
    """Check we reset concentrations"""

    testpatient = propofol.Schnider(40, 80, 180, 'm')
    old_conc = {"ox1": testpatient.x1, "ox2": testpatient.x2, "ox3": testpatient.x3, "oxeo": testpatient.xeo}
    testpatient.give_drug(200)
    testpatient.reset_concs(old_conc)

    assert(testpatient.x1) == 0

def test_effect():
    """test effect site targetting bolus """
    testpatient = propofol.Schnider(40, 70, 190, 'm')
    assert testpatient.effect_bolus(6) == 95.6