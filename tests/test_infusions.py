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

def test_plasma_infusion():
    """ basic test for plasma infusion """
    testpatient = propofol.Marsh(70)
    assert testpatient.plasma_infusion(2, 60) == [3.27269899102373, 0.1453355022895698, 0.14478000490919285, 0.14422948797801816, 0.1436839059972244, 0.143143213884116]
