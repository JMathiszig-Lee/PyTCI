from PyTCI.models import dexmedetomidine


def test_hannivoort():
    """ values come from original development paper 
    Development of an Optimized Pharmacokinetic Model of Dexmedetomidine Using Target-controlled Infusion in Healthy Volunteers
    Anesthesiology 8 2015, Vol.123, 357-367. doi:10.1097/ALN.0000000000000740 
    """
    testpatient = dexmedetomidine.Hannivoort(70)

    assert testpatient.v1 == 1.78
    assert testpatient.v2 == 30.3
    assert testpatient.v3 == 52.0

    assert testpatient.Q1 == 0.686
    assert testpatient.Q2 == 2.98
    assert testpatient.Q3 == 0.602